# domain/entities/event.py

class Event:
    def __init__(self, id, name, description, place, date_time, participant_limit, host_id, host_name, participant_count = 0, status="active"):
        self.id = id
        self.name = name
        self.description = description
        self.place = place
        self.date_time = date_time
        self.participant_limit = participant_limit
        self.host_id = host_id
        self.host_name = host_name
        self.participant_count = participant_count
        self.status = status
