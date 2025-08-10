"""
Example of how to properly handle async callbacks with LiveKit's .on() method.

The error you're seeing occurs because LiveKit's .on() method expects synchronous callbacks,
not async ones. When you need to perform async operations in response to events,
you should use a synchronous callback that creates an asyncio task.
"""

import asyncio
from livekit.agents import JobContext


async def example_entrypoint(ctx: JobContext) -> None:
    await ctx.connect()
    
    # ❌ WRONG: This will cause the error you're seeing
    # @ctx.room.on("participant_connected")
    # async def handle_participant_connected(participant):
    #     await some_async_operation(participant)
    
    # ✅ CORRECT: Use a synchronous callback that creates an asyncio task
    def handle_participant_connected(participant):
        # Create an asyncio task to handle the async operation
        asyncio.create_task(some_async_operation(participant))
    
    # Register the synchronous callback
    ctx.room.on("participant_connected", handle_participant_connected)
    
    # Alternative pattern using lambda (for simple cases)
    ctx.room.on("participant_disconnected", lambda participant: asyncio.create_task(
        handle_participant_disconnected(participant)
    ))


async def some_async_operation(participant):
    """Example async operation that might take time."""
    print(f"Processing participant: {participant.identity}")
    await asyncio.sleep(1)  # Simulate some async work
    print(f"Finished processing {participant.identity}")


async def handle_participant_disconnected(participant):
    """Example async operation for participant disconnection."""
    print(f"Participant {participant.identity} disconnected")
    # Perform cleanup or other async operations
    await asyncio.sleep(0.5)


# More complex example with error handling
def handle_participant_connected_with_error_handling(participant):
    async def wrapped_operation():
        try:
            await some_async_operation(participant)
        except Exception as e:
            print(f"Error processing participant {participant.identity}: {e}")
    
    asyncio.create_task(wrapped_operation())


# Example with multiple async operations
def handle_complex_participant_event(participant):
    async def complex_operation():
        # Perform multiple async operations
        await asyncio.gather(
            some_async_operation(participant),
            another_async_operation(participant),
            third_async_operation(participant)
        )
    
    asyncio.create_task(complex_operation())


async def another_async_operation(participant):
    """Another example async operation."""
    print(f"Another operation for {participant.identity}")
    await asyncio.sleep(0.5)


async def third_async_operation(participant):
    """Third example async operation."""
    print(f"Third operation for {participant.identity}")
    await asyncio.sleep(0.3)