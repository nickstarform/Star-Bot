package io.ph.bot.events;

public class CustomEventDispatcher {
    public void dispatch(BotEvent e) {
        e.handle();
    }
}
