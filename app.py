from beam import function

@function()
def handler():
    return {}

if __name__ == "__main__":
    # Runs locally
    handler.local()
    # Runs on the cloud
    handler.remote()
