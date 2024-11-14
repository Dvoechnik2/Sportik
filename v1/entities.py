from dataclasses import dataclass


class Event(dataclass):
    id : int
    name : str
    description : str
    place : str
    date_time : str
    participant_limit : int | None
    participant_count : int | None
    host_id: int
    host_name : str
    status : str


class User(dataclass):
    id : int
    name : str


class Sercified_user(User):
    confimation: bool