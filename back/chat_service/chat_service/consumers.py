import asyncio
import typing
import json
import logging

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async

from .models import Room, Message
# from .utils.elapsed_time import elapsed_time
# from .utils.rooms import is_user_room_member

class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        pass

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        pass
    
    #     self.user = self.scope['user']
    #     self._logClassIdentifier = self.user.username

    #     if self.user.is_authenticated:
    #         rooms = await self.get_user_rooms()

    #         for room in rooms:
    #             await self.channel_layer.group_add(
    #                 f'chat_{room.id}',
    #                 self.channel_name
    #             )

    #         await self.channel_layer.group_add(
    #             f'chat_user_{self.user.id}',
    #             self.channel_name
    #         )

    #         await self.accept()

    #     else:
    #         await self.close()


    # async def disconnect(self, close_code):
    #     if self.user.is_authenticated:
    #         rooms = await self.get_user_rooms()
    #         for room in rooms:
    #             await self.channel_layer.group_discard(
    #                 f'chat_{room.id}',
    #                 self.channel_name
    #             )

    #         await self.channel_layer.group_discard(
    #             f'chat_user_{self.user.id}',
    #             self.channel_name
    #         )

    # async def receive(self, text_data):
    #     data = json.loads(text_data)
    #     logging.info(f"received: {data}")

    #     message_type = data.get('type')
    #     room_id = data.get('room_id')

    #     room = await database_sync_to_async(ChatRoom.objects.get)(id=room_id)
    #     is_member = await database_sync_to_async(room.is_in_room)(self.user)

    #     if not is_member:
    #         logging.error(f"{self.user} not in room {room.id}")
    #         return

    #     if message_type == 'send_message':
    #         await self.send_message(data)

    #     elif message_type == 'send_invitation':
    #         await self.send_invitation(data)

    #     elif message_type == 'cancel_invitation':
    #         await self.cancel_invitation(data)

    #     elif message_type == 'cancel_all_invitations':
    #         await self.cancel_all_invitations(data)

    #     elif message_type == 'decline_invitation':
    #         await self.decline_invitation(data)

    #     elif message_type == 'accept_invitation':
    #         await self.accept_invitation(data)

    #     elif message_type == 'create_room':
    #         await self.create_room(data)

    #     elif message_type == 'join_room':
    #         await self.join_room(data)

    #     elif message_type == 'quit_room':
    #         await self.quit_room(data)


    # async def send_invitation(self, data):
    #     try:
    #         room_id = data.get('room_id')
    #         room = await database_sync_to_async(
    #             ChatRoom.objects.get
    #         )(id=room_id)

    #         existing_invitations = await database_sync_to_async(
    #             list
    #         )(Invitation.objects.filter(sender=self.user, room=room, status='pending'))


    #         # Loop through each existing invitation
    #         for invitation in existing_invitations:
    #             invitation.status='canceled'
    #             await database_sync_to_async(invitation.save)()

    #             await self.channel_layer.group_send(
    #                 f'chat_{room.id}',
    #                 {
    #                     'type': 'invitation',
    #                     'id': invitation.id,
    #                     'room_id': room.id,
    #                     'status': invitation.status,
    #                     'sender': self.user.toJSON()
    #                 }
    #             )


    #         invitation = await database_sync_to_async(
    #             Invitation.objects.create
    #         )(room=room, sender=self.user)

    #         logging.info(invitation)

    #         await self.channel_layer.group_send(
    #             f'chat_{room.id}',
    #             {
    #                 'type': 'invitation',
    #                 'id': invitation.id,
    #                 'room_id': room_id,
    #                 'status': invitation.status,
    #                 'sender': self.user.toJSON()
    #             }
    #         )

    #     except Exception as e:
    #         logging.info(f'error {e}')


    # async def cancel_invitation(self, data):
    #     try:
    #         room_id = data.get('room_id')
    #         invitation_id = data.get('invitation_id')

    #         room = await database_sync_to_async(
    #             ChatRoom.objects.get
    #         )(id=room_id)

    #         invitation = await database_sync_to_async(
    #             Invitation.objects.get
    #         )(id=invitation_id)

    #         invitation_sender = await database_sync_to_async(lambda: invitation.sender)()

    #         invitation_room = await database_sync_to_async(lambda: invitation.room)()

    #         if invitation_sender != self.user:
    #             return
    #         elif invitation_room.id != room.id:
    #             return

    #         invitation.status = 'canceled'
    #         await database_sync_to_async(invitation.save)()

    #         await self.channel_layer.group_send(
    #             f'chat_{room.id}',
    #             {
    #                 'type': 'invitation',
    #                 'id': invitation.id,
    #                 'room_id': room_id,
    #                 'status': invitation.status,
    #                 'sender': self.user.toJSON()
    #             }
    #         )

    #     except Exception as e:
    #         logging.error(f'error: {e}')


    # async def cancel_all_invitations(self, data):
    #     try:
    #         room_id = data.get('room_id')
    #         room = await database_sync_to_async(
    #             ChatRoom.objects.get
    #         )(id=room_id)

    #         existing_invitations = await database_sync_to_async(
    #             list
    #         )(Invitation.objects.filter(sender=self.user, room=room, status='pending'))

    #         for invitation in existing_invitations:
    #             invitation.status='canceled'
    #             await database_sync_to_async(invitation.save)()

    #             await self.channel_layer.group_send(
    #                 f'chat_{room.id}',
    #                 {
    #                     'type': 'invitation',
    #                     'id': invitation.id,
    #                     'room_id': room.id,
    #                     'status': invitation.status,
    #                     'sender': self.user.toJSON()
    #                 }
    #             )

    #     except Exception as e:
    #         logging.error(f'error: {e}')


    # async def decline_invitation(self, data):
    #     try:
    #         room_id = data.get('room_id')
    #         invitation_id = data.get('invitation_id')

    #         room = await database_sync_to_async(
    #             ChatRoom.objects.get
    #         )(id=room_id)

    #         logging.info(room)

    #         invitation = await database_sync_to_async(
    #             Invitation.objects.get
    #         )(id=invitation_id)

    #         invitation_sender = await database_sync_to_async(lambda: invitation.sender)()

    #         if invitation_sender == self.user:
    #             return

    #         logging.info(f'sender and user not equal')

    #         invitation_room = await database_sync_to_async(lambda: invitation.room)()

    #         if invitation_room.id != room.id:
    #             return

    #         logging.info(f'inivtation is in the right room')

    #         invitation.status = 'declined'
    #         await database_sync_to_async(invitation.save)()

    #         logging.info(f'update invitation status')

    #         await self.channel_layer.group_send(
    #             f'chat_{room.id}',
    #             {
    #                 'type': 'invitation',
    #                 'id': invitation.id,
    #                 'room_id': room_id,
    #                 'status': invitation.status,
    #                 'sender': invitation_sender.toJSON()
    #             }
    #         )

    #     except Exception as e:
    #         logging.error(f'error: {e}')

    # async def accept_invitation(self, data):
    #     try:
    #         room_id = data.get('room_id')
    #         invitation_id = data.get('invitation_id')

    #         room = await database_sync_to_async(
    #             ChatRoom.objects.get
    #         )(id=room_id)

    #         invitation = await database_sync_to_async(
    #             Invitation.objects.get
    #         )(id=invitation_id)

    #         if invitation.status != 'pending':
    #             return

    #         invitation_sender = await database_sync_to_async(lambda: invitation.sender)()

    #         if invitation_sender == self.user:
    #             return

    #         invitation_room = await database_sync_to_async(lambda: invitation.room)()

    #         if invitation_room.id != room.id:
    #             return

    #         invitation.status = 'accepted'
    #         invitation.game = await database_sync_to_async(Game.objects.create)()
    #         await database_sync_to_async(invitation.game.players.add)(self.user, invitation.sender)
    #         await database_sync_to_async(invitation.save)()

    #         await self.channel_layer.group_send(
    #             f'chat_{room.id}',
    #             {
    #                 'type': 'invitation',
    #                 'id': invitation.id,
    #                 'room_id': room_id,
    #                 'status': invitation.status,
    #                 'sender': invitation_sender.toJSON(),
    #                 'game_id': invitation.game.id
    #             }
    #         )

    #     except Exception as e:
    #         logging.error(f'error: {e}')


    # async def invitation(self, data):
    #     await self.send_json(data)


    # async def send_message(self, data):
    #     content = data.get('content')
    #     room_id = data.get('room_id')

    #     try:
    #         room = await database_sync_to_async(ChatRoom.objects.get)(id=room_id)
    #         message = await database_sync_to_async(
    #             Message.objects.create
    #         )(room=room, user=self.user, content=content)

    #         message_data = {
    #             'type':      'message',
    #             'room_id':   message.room.id,
    #             'sender':    message.user.toJSON(),
    #             'content':   message.content,
    #             'timestamp': elapsed_time(message.timestamp)
    #         }

    #         await self.channel_layer.group_send(
    #             f'chat_{room.id}',
    #             message_data
    #         )

    #     except ChatRoom.DoesNotExist:
    #         await self.send(text_data=json.dumps({
    #             'error': 'Room does not exist'
    #         }))


    # async def message(self, data: dict):
    #     await self.send_json(data)


    # async def create_room(self, data):
    #     try:
    #         user_ids = data.get('users', [])

    #         if self.user.id not in user_ids:
    #             user_ids.append(self.users.id)

    #         room = await database_sync_to_async(ChatRoom.objects.create)(
    #             is_private=False
    #         )

    #         # Add the users to the room
    #         for user_id in user_ids:
    #             await self.channel_layer.group_send(
    #                 f'chat_user_{user_id}',
    #                 {
    #                     'type': 'join_room',
    #                     'room_id': room.id
    #                 }
    #             )

    #     except Exception as e:
    #         logging.info(f'error: {e}')


    # async def join_room(self, data):
    #     try:
    #         room_id = data.get('room_id')
    #         room = await database_sync_to_async(ChatRoom.objects.get)(id=room_id)

    #         await database_sync_to_async(room.users.add)(self.user)

    #         await self.channel_layer.group_add(
    #             f'chat_{room.id}',
    #             self.channel_name
    #         )

    #         await self.send_json({
    #             'action': 'room_joined',
    #             'room_id': room.id
    #         })

    #     except ChatRoom.DoesNotExist:
    #         await self.send(text_data=json.dumps({
    #             'error': 'Room does not exist'
    #         }))


    # async def quit_room(self, data):
    #     room_id = data.get('room_id')
    #     try:
    #         room = await database_sync_to_async(
    #             ChatRoom.objects.get
    #         )(id=room_id)

    #     except ChatRoom.DoesNotExist:
    #         await self.send(text_data=json.dumps({
    #             'error': 'Room does not exist'
    #         }))

    # async def quit_room_response(self, data):
    #     await self.send(text_data=json.dumps({
    #         'action':  'room_quit',
    #         'room_id': data['room_id']
    #     }))


    # # get all rooms of an user
    # @database_sync_to_async
    # def get_user_rooms(self):
    #     rooms = self.user.rooms.all()
    #     return list(rooms)

    # # save a message in the db
    # @database_sync_to_async
    # def save_message(self, room, user, message, is_duel=False):
    #     message = Message.objects.create(room=room, user=user, content=message, is_duel=is_duel)
    #     message.save()

    #     return message
