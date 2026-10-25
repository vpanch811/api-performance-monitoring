from typing import Literal
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.performance.tester import (
    run_concurrent_test,
    run_performance_test,
)

from app.performance.reporter import (
    generate_performance_report,
)

from app.performance.history import (
    add_performance_report,
    get_performance_history,
    get_performance_summary,
    get_load_level_comparison,
    detect_performance_regression,
)

from app.database import initialize_database, save_report, get_saved_reports

app = FastAPI(
    title="API Performance Monitoring System",
    description="REST API for performance testing and deployment monitoring",
    version="1.0.0"
)
initialize_database()

class UserCreate(BaseModel):
    name: str
    email: EmailStr


class User(UserCreate):
    id: int


class PerformanceTestRequest(BaseModel):
    url: str
    number_of_requests: int = Field(
        default=10,
        ge=1,
        le=100
    )
    mode: Literal["sequential", "concurrent"] = "sequential"

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        parsed_url = urlparse(value)

        if parsed_url.scheme not in ("http", "https"):
            raise ValueError(
                "URL must use http or https"
            )

        if not parsed_url.netloc:
            raise ValueError(
                "Invalid URL"
            )

        return value


users = [
    User(
        id=1,
        name="Alice",
        email="alice@example.com"
    ),
    User(
        id=2,
        name="Bob",
        email="bob@example.com"
    )
]


@app.get("/")
def root():
    return {
        "message": "API Performance Monitoring System is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.get("/users")
def get_users():
    return users


@app.get("/users/{user_id}")
def get_user(user_id: int):
    for user in users:
        if user.id == user_id:
            return user

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )


@app.post(
    "/users",
    response_model=User,
    status_code=status.HTTP_201_CREATED
)
def create_user(user: UserCreate):
    new_id = max(
        user.id for user in users
    ) + 1 if users else 1

    new_user = User(
        id=new_id,
        name=user.name,
        email=user.email
    )

    users.append(new_user)

    return new_user


@app.put(
    "/users/{user_id}",
    response_model=User
)
def update_user(
    user_id: int,
    updated_user: UserCreate
):
    for index, user in enumerate(users):
        if user.id == user_id:
            updated = User(
                id=user_id,
                name=updated_user.name,
                email=updated_user.email
            )

            users[index] = updated

            return updated

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )


@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    for index, user in enumerate(users):
        if user.id == user_id:
            users.pop(index)

            return {
                "message": "User deleted successfully"
            }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )

@app.post("/performance-test")
async def performance_test(
    request: PerformanceTestRequest
):
    if request.mode == "sequential":
        performance_result = run_performance_test(
            request.url,
            request.number_of_requests
        )

    elif request.mode == "concurrent":
        performance_result = await run_concurrent_test(
            request.url,
            request.number_of_requests
        )

    report = generate_performance_report(performance_result)
    add_performance_report(report)
    return report

@app.get("/performance-history")
def performance_history():
    reports = get_saved_reports()

    return {
        "total_tests": len(reports),
        "tests": [
            {"report": report}
            for report in reports
        ],
    }

@app.get("/performance-summary")
async def performance_summary():
    return get_performance_summary()

@app.get("/performance-comparison")
async def performance_comparison():
    return {
        "total_tests": len(get_load_level_comparison()),
        "tests": get_load_level_comparison()
    }

@app.get("/performance-regression")
def performance_regression(
    regression_threshold_percent: float = 50.0,
    ):
    if regression_threshold_percent < 0:
        raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Regression threshold cannot be negative",
        )

    return detect_performance_regression(
        regression_threshold_percent=regression_threshold_percent
    )
