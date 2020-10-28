package io.ph.bot.commands.moderation;

import java.awt.Color;
import java.time.Instant;

import io.ph.bot.commands.Command;
import io.ph.bot.commands.CommandCategory;
import io.ph.bot.commands.CommandData;
import io.ph.bot.model.GuildObject;
import io.ph.bot.model.Permission;
import io.ph.util.Util;
import io.ph.util.MessageUtils;
import net.dv8tion.jda.api.EmbedBuilder;
import net.dv8tion.jda.api.entities.Message;
import net.dv8tion.jda.api.managers.AudioManager;
/**
 * Force Bot to leave your server's voice channel if she's in it
 * @author Nick
 *
 */
@CommandData (
        defaultSyntax = "leave",
        aliases = {},
        category = CommandCategory.MUSIC,
        permission = Permission.KICK,
        description = "Force Bot to leave voice channel. This also kills the queue",
        example = "(no parameters)"
        )
public class Leave extends Command {
    
    @Override
    public void executeCommand(Message msg) {
        EmbedBuilder em = new EmbedBuilder().setTimestamp(Instant.now());
        AudioManager audio = msg.getGuild().getAudioManager();
        audio.closeAudioConnection();
        GuildObject.guildMap.get(msg.getGuild().getId()).getMusicManager().reset();
        
        em.setTitle("Success", null)
        .setColor(Util.resolveColor(Util.memberFromMessage(msg), Color.GREEN))
        .setDescription("Left your voice channel and cleared the queue");
        MessageUtils.sendMessage(msg.getChannel().getId(),em.build(),5);
        msg.delete().queue();
    }

}
