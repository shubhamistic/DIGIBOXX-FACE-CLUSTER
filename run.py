import sys
import socketio
from clustering_handler import handle_clustering


# define socket client
sio = socketio.Client()
url = None
jwt_token = None


def connect_to_server(url, authorization_key):
    try:
        # connect to the server
        sio.connect(
            f"{url}?Authorization={authorization_key}",
            namespaces=['/daemon']
        )
        if sio.sid:
            return {
                "connected": True,
                "sid": sio.sid
            }
        else:
            return {"connected": False}
    except Exception as error:
        return {
            "connected": False,
            "error": error
        }


# server will send the clustering task on this event
@sio.on('task', namespace='/daemon')
def task_event(data):
    task_info = data["task_info"]
    cluster_dict = data["cluster_dict"]
    clustering_result = handle_clustering(
        url=url,
        jwt_token=f"Bearer {jwt_token}",
        task_info=task_info,
        cluster_dict=cluster_dict
    )
    # emit the task completed event
    emit_task_completed_event(
        task_info=task_info,
        result=clustering_result
    )


# if server fails to authorize the client
@sio.on('authorized', namespace='/daemon')
def authorized_event(data):
    global jwt_token
    print(data["message"])
    jwt_token = data["jwt_token"]


# if server fails to authorize the client
@sio.on('unauthorized', namespace='/daemon')
def unauthorized_event(data):
    print(data["message"])
    sio.disconnect()
    sys.exit(1)


# the client will emit the clustering task through this method
def emit_task_completed_event(task_info, result):
    sio.emit(
        'task_completed',
        {
            "message": "Success: task successfully completed!",
            "task_info": task_info,
            "clustering_result": result
        },
        namespace='/daemon'
    )


@sio.on('connect', namespace='/daemon')
def on_connect():
    print("Connected to Server Successfully!")


@sio.on('disconnect', namespace='/daemon')
def on_disconnect():
    print("Disconnected!")
    sys.exit(1)


if __name__ == "__main__":
    # Check if the correct number of arguments is provided
    if len(sys.argv) != 3:
        print("Error (Usage): python run.py server-url daemon-authorization-key")
        sys.exit(1)

    url = sys.argv[1]
    daemon_authorization_key = sys.argv[2]

    # connect to socket
    print("Connecting to server on url:", url)
    socket_connect_response = connect_to_server(url, daemon_authorization_key)
    if not socket_connect_response["connected"]:
        print("Error: error connecting to server!")
        sys.exit(1)

    # run the socket loop
    sio.wait()
