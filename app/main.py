def handler(event, context=None):
    return {
        "status": "ok",
        "message": "Retail Ops Agent bootstrap successful"
    }


if __name__ == "__main__":
    print(handler({}))
