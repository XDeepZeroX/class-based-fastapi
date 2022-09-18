import uvicorn

if __name__ == "__main__":
    # generics
    # uvicorn.run('runs.generics:app', host="localhost", port=8001, reload=True, debug=True)

    # simple controller
    uvicorn.run('runs.simple_controller:app', host="localhost", port=8001, reload=True, debug=True)
