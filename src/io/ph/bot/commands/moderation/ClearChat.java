package io.ph.bot.commands.moderation;

import java.awt.Color;
import java.time.Instant;

import io.ph.bot.commands.Command;
import io.ph.bot.commands.CommandCategory;
import io.ph.bot.commands.CommandData;
import io.ph.bot.model.Permission;
import io.ph.util.MessageUtils;
import io.ph.util.Util;
import net.dv8tion.jda.api.EmbedBuilder;
import net.dv8tion.jda.api.entities.Message;
import net.dv8tion.jda.api.entities.TextChannel;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;


/**
 * Clear channel messages(default 5000)
 * @author Nick
 */
@CommandData (
        defaultSyntax = "clearchat",
        aliases = {"clearchannel"},
        category = CommandCategory.MODERATION,
        permission = Permission.MANAGE_CHANNELS,
        description = "Clears the entire channels history. Maxes at 5000 messages by default",
        example = "(no options, no further prompts)"
                + "all *keeps attempting to remove messages until channel is empty"
        )
public class ClearChat extends Command {

    private static final int MAX = 50; // # of 100 message iterations

    @Override
    public void executeCommand(Message msg) {
        EmbedBuilder em = new EmbedBuilder().setTimestamp(Instant.now());
        String t = Util.getCommandContents(msg);
        TextChannel textChannel = msg.getTextChannel();
        List<Message> hist = msg.getTextChannel().getHistory().retrievePast(100).complete();
        AtomicInteger index = new AtomicInteger(0);
        String param = "";

        try{
            param = Util.getParam(msg);
        } catch (IndexOutOfBoundsException e) {
            param = "";
        }   

        while (!hist.isEmpty()){
            index.incrementAndGet();
            // debug
            //System.out.println("deleteIds: " + deleteIds);
            try {
                textChannel.deleteMessages(hist).complete();
            } catch (IllegalArgumentException ex) {
                for (int i = 0; i < hist.size(); i++) {
                    String id = hist.get(i).getId();
                    textChannel.deleteMessageById(id).complete();
                }
            }
            hist.clear();
            hist = msg.getTextChannel().getHistory().retrievePast(100).complete();
            if ((index.get() >= MAX) && (!param.equals("all"))) {
                hist.clear();
            }
        }

        em.setTitle("Success", null)
        .setColor(Util.resolveColor(Util.memberFromMessage(msg), Color.GREEN))
        .setDescription("Cleared channel");
        MessageUtils.sendMessage(msg.getChannel().getId(),em.build(),5);
        msg.delete().queue();
    }

}
