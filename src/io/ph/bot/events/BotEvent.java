package io.ph.bot.events;

import net.dv8tion.jda.core.entities.Guild;

public abstract class BotEvent {
    Guild guild;
    
    public BotEvent(Guild guild) {
        this.guild = guild;
    }
    
    public Guild getGuild() {
        return this.guild;
    }
    
    public abstract void handle();
}
