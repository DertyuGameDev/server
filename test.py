import requests

# print(requests.post('https://bot-production-1a86.up.railway.app/json',
#                           json={'user1': 1866856400, 'user2': 375774305}).text)

print(requests.post('https://api.telegram.org/bot7792799952:AAGSWn1ZgmC9CJFm3W1FhIq98tMJiZbzJLo/getUpdates', params={
    "update_id": 850612308,
    "message": {
        "message_id": 3439897,
        "from": {
            "id": 1866856400,
            "is_bot": False,
            "first_name": "DertyuDev",
            "username": "DertyuDev",
            "language_code": "ru"
        },
        "chat": {
            "id": 1866856400,
            "first_name": "DertyuDev",
            "username": "DertyuDev",
            "type": "private"
        },
        "date": 1746460335,
        "text": "sdf"
    }
}
).text)