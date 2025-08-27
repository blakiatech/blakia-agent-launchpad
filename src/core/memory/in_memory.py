# core/memory/in_memory.py


class InMemoryHistory:
    def __init__(self):
        # clave: session_id -> lista de ModelMessage
        self._store: dict[str, list] = {}

    def get(self, sid: str):
        # devuelve SIEMPRE una lista (copia para no “pisarla” fuera)
        return list(self._store.get(sid, []))

    def add(self, sid: str, messages):
        if not messages:
            return
        # Asegura que hay una lista REAL dentro del diccionario
        bucket = self._store.setdefault(sid, [])
        if isinstance(messages, list):
            bucket.extend(messages)
        else:
            bucket.append(messages)

    # Muy útil para guardar el historial completo de golpe
    def set(self, sid: str, messages):
        if not messages:
            self._store[sid] = []
        elif isinstance(messages, list):
            self._store[sid] = list(messages)
        else:
            self._store[sid] = [messages]

    def clear(self, sid: str):
        self._store.pop(sid, None)


# instancia global
memory_store = InMemoryHistory()
