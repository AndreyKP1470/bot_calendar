class Calendar:
    def __init__(self):
        # Словарь для хранения событий: ключ — id, значение — детали события.
        self.events = {}

    def create_event(self, event_name:str, event_date:str, event_time:str, event_details:str) -> int:
        """
        Создаёт новое событие.
        :param event_name: Название события.
        :param event_date: Дата события (строка в формате 'YYYY-MM-DD').
        :param event_time: Время события (строка в формате 'HH:MM').
        :param event_details: Описание события.
        :return: ID созданного события.
        """

        event_id = len(self.events) + 1
        event = {
            "id": event_id,
            "name": event_name,
            "date": event_date,
            "time": event_time,
            "details": event_details
        }
        self.events[event_id] = event
        return event_id

    def get_event(self, event_id: int) -> dict | None: 
      """Возвращает событие по его идентификатору.
      Args:
          event_id (int): Идентификатор события.
      Returns:
         dict или None: Словарь с деталями события, если оно найдено, иначе None.
      """
      return self.events.get(event_id)

    def update_event(self, event_id:int, **kwargs) -> bool:
        """Обновляет событие по его идентификатору."""
        event = self.events.get(event_id)
        if event:
            event.update(kwargs)
            return True
        return False

    def delete_event(self, event_id:int) -> bool:
        """Удаляет событие по его идентификатору."""
        if event_id in self.events:
            del self.events[event_id]
            return True
        return False

    def get_all_events(self) -> str:
        """Возвращает имена всех событий"""
        name_events = "\n".join(
        event["name"] for event in self.events.values()
        if event.get("name")
        )
        return name_events