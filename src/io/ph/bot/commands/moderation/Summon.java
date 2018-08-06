package io.ph.bot.commands.moderation;

import java.awt.Color;
import java.time.Instant;
import java.util.Optional;

import io.ph.bot.commands.Command;
import io.ph.bot.commands.CommandCategory;
import io.ph.bot.commands.CommandData;
import io.ph.bot.model.Permission;
import io.ph.util.Util;
import net.dv8tion.jda.core.EmbedBuilder;
import net.dv8tion.jda.core.entities.Message;
import net.dv8tion.jda.core.entities.VoiceChannel;
/**
 * Summon the bot into a channel of your choosing
 * @author Nick
 *
 */
@CommandData (
        defaultSyntax = "summon",
        aliases = {},
        category = CommandCategory.MUSIC,
        permission = Permission.KICK,
        description = "Summon Bot into your voice channel",
        example = "Summons to channel"
        )
public class Summon extends Command {
    
    @Override
    public void executeCommand(Message msg) {
        EmbedBuilder em = new EmbedBuilder().setTimestamp(Instant.now());
        String command = Util.getCommandContents(msg).toLowerCase();
        Optional<VoiceChannel> opt;
        net.dv8tion.jda.core.managers.AudioManager audio = msg.getGuild().getAudioManager();

        // argument not specified
        if ((opt = msg.getGuild().getVoiceChannels().stream()
                .filter(v -> v.getMembers().contains(msg.getGuild().getMember(msg.getAuthor())))
                .findAny()).isPresent()) {
            // User is in a channel, calling the play method
            audio.openAudioConnection(opt.get());
        } else if (msg.getGuild().getVoiceChannelsByName(command,true).size() > 0 ) {
            audio.openAudioConnection(msg.getGuild().getVoiceChannelsByName(command,true).get(0));
        } else {
            // User isn't in a channel, yell at them
            em.setTitle("Error", null)
            .setColor(Color.RED)
            .setDescription("You must be in a voice channel so I know where to go!");
            msg.getChannel().sendMessage(em.build()).queue();
            return;
        }
        if (msg.getGuild().getAudioManager().isConnected()
                && msg.getGuild().getAudioManager().getConnectedChannel().equals(opt.get())) {
            em.setTitle("Hmm...", null)
            .setColor(Util.resolveColor(Util.memberFromMessage(msg), Color.MAGENTA))
            .setDescription("I'm already in your voice channel!");
            msg.getChannel().sendMessage(em.build()).queue();
            return;
        }
        audio.openAudioConnection(opt.get());
        em.setTitle("Success", null)
        .setColor(Util.resolveColor(Util.memberFromMessage(msg), Color.GREEN))
        .setDescription("Joined your voice channel");
        msg.getChannel().sendMessage(em.build()).queue();
    }

}
