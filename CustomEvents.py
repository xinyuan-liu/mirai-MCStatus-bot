from graia.broadcast.entities.event import BaseEvent
from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.interfaces.dispatcher import DispatcherInterface

class ServerUpdateEvent(BaseEvent):
    message: str 
    def __init__(self, message):
        super().__init__(message=message)
    
    class Dispatcher(BaseDispatcher):
        # def catch(self, interface: DispatcherInterface) -> Any:
        #     return ...

        async def catch(self, interface: DispatcherInterface):
            return ...

if __name__=='__main__':
    pass
