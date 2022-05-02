from aiogram import types


class Config:
    TOKEN = "token"
    LEVELS = {
        1: 0,
        2: 3,
        3: 10,
        4: 20,
        5: 25,
        6: 28
    }
    LEVELS_action_points = {
        1: 0,
        2: 2,
        3: 3,
        4: 5,
        5: 7,
        6: 10
    }

    LEVELS_for_PERMISIONS = {
        1: types.ChatPermissions(can_send_messages=True,
                                 can_send_media_messages=False,
                                 can_send_polls=False,
                                 can_send_other_messages=False,
                                 can_add_web_page_previews=False,
                                 can_change_info=False,
                                 can_invite_users=False,
                                 can_pin_messages=False
                                 ),

        2: types.ChatPermissions(can_send_messages=True,
                                 can_send_media_messages=False,
                                 can_send_polls=False,
                                 can_send_other_messages=False,
                                 can_add_web_page_previews=False,
                                 can_change_info=False,
                                 can_invite_users=True,
                                 can_pin_messages=False
                                 ),
        3: types.ChatPermissions(can_send_messages=True,
                                 can_send_media_messages=True,
                                 can_send_polls=False,
                                 can_send_other_messages=False,
                                 can_add_web_page_previews=False,
                                 can_change_info=False,
                                 can_invite_users=True,
                                 can_pin_messages=False
                                 ),
        4: types.ChatPermissions(can_send_messages=True,
                                 can_send_media_messages=True,
                                 can_send_polls=False,
                                 can_send_other_messages=False,
                                 can_add_web_page_previews=True,
                                 can_change_info=False,
                                 can_invite_users=True,
                                 can_pin_messages=False
                                 ),
        5: types.ChatPermissions(can_send_messages=True,
                                 can_send_media_messages=True,
                                 can_send_polls=True,
                                 can_send_other_messages=False,
                                 can_add_web_page_previews=True,
                                 can_change_info=False,
                                 can_invite_users=True,
                                 can_pin_messages=False
                                 ),
        6: types.ChatPermissions(can_send_messages=True,
                                 can_send_media_messages=True,
                                 can_send_polls=True,
                                 can_send_other_messages=True,
                                 can_add_web_page_previews=True,
                                 can_change_info=False,
                                 can_invite_users=True,
                                 can_pin_messages=False
                                 ),
    }
    MAX_LEVEL = 6
