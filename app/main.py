
from app.services.decision_service import run_agent


def handler(event, context=None):
    return run_agent(event)


if __name__ == "__main__":
    response = handler({})
    print(response)

