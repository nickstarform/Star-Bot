package io.ph.bot.listeners;

import java.awt.Color;
import java.time.Instant;

import io.ph.bot.model.GuildObject;
import net.dv8tion.jda.api.EmbedBuilder;
import net.dv8tion.jda.api.entities.TextChannel;
import net.dv8tion.jda.api.events.guild.GuildBanEvent;
import net.dv8tion.jda.api.events.guild.GuildUnbanEvent;
import net.dv8tion.jda.api.hooks.ListenerAdapter;

public class ModerationListeners extends ListenerAdapter {
    
    @Override
    public void onGuildBan(GuildBanEvent e) {
        GuildObject g = GuildObject.guildMap.get(e.getGuild().getId());
        TextChannel ch;
        if (!g.getSpecialChannels().getLog().isEmpty()
                && (ch = e.getGuild().getTextChannelById(g.getSpecialChannels().getLog())) != null) {
            EmbedBuilder em = new EmbedBuilder();
            em.setAuthor(e.getUser().getName() + " has been banned", null, e.getUser().getAvatarUrl())
            .setColor(Color.RED)
            .setTimestamp(Instant.now());
            ch.sendMessage(em.build()).queue();
        }
    }
    
    @Override
    public void onGuildUnban(GuildUnbanEvent e) {
        GuildObject g = GuildObject.guildMap.get(e.getGuild().getId());
        TextChannel ch;
        if (!g.getSpecialChannels().getLog().isEmpty()
                && (ch = e.getGuild().getTextChannelById(g.getSpecialChannels().getLog())) != null) {
            EmbedBuilder em = new EmbedBuilder();
            em.setAuthor(e.getUser().getName() + " has been unbanned", null, e.getUser().getAvatarUrl())
            .setColor(Color.GREEN)
            .setTimestamp(Instant.now());
            ch.sendMessage(em.build()).queue();
        }
    }
}
