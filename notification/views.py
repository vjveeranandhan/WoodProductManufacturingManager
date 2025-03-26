from firebase_admin import messaging

def send_push_notification(token, title, message, data=None):
    """
    Sends a push notification using Firebase Cloud Messaging.
    
    :param token: FCM device token (string)
    :param title: Notification title (string)
    :param message: Notification body (string)
    :param data: Additional data as a dictionary (optional)
    """
    try:
        # Create message object
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=message,
            ),
            data=data or {},
            token=token,
        )

        # Send message
        response = messaging.send(message)
        return response

    except Exception as e:
        print(f"Error sending push notification: {e}")
        return None
