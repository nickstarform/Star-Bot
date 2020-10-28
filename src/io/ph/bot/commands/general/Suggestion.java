package io.ph.bot.commands.general;

import java.awt.Color;
import java.util.stream.Collectors;

import io.ph.bot.Bot;
import io.ph.bot.commands.Command;
import io.ph.bot.commands.CommandCategory;
import io.ph.bot.commands.CommandData;
import io.ph.bot.model.Permission;
import io.ph.util.Util;
import io.ph.util.MessageUtils;
import net.dv8tion.jda.api.EmbedBuilder;
import net.dv8tion.jda.api.entities.Member;
import net.dv8tion.jda.api.entities.Message;
import net.dv8tion.jda.api.entities.User;
import java.time.ZoneId;
import java.util.Date;
import java.text.SimpleDateFormat;
import net.dv8tion.jda.api.JDA;
/**
 * Send suggestion to creator
 * @author Nick
 */
@CommandData (
        defaultSyntax = "suggestion",
        aliases = {"suggest","suggestions"},
        category = CommandCategory.UTILITY,
        permission = Permission.NONE,
        description = "Send a PM to the developer with suggestions\n"
                    + "Please be descriptive with your ideas\n"
                    + "Please be patient and wait for a reply\n"
        ,
        example = "Add love functionality, !love user to send :heart: to them"
        )
public class Suggestion extends Command {

    @Override
    public void executeCommand(Message msg) {
        EmbedBuilder em = new EmbedBuilder();
        if(msg.getContentDisplay().split(" ").length < 1) {
            MessageUtils.sendIncorrectCommandUsage(msg, this);
            return;
        }
        String suggestContents = Util.getCommandContents(msg);
        if(suggestContents.length() > 500) {
            em.setTitle("Error", null)
            .setColor(Color.RED)
            .addField("",suggestContents,false)
            .setDescription("Maximum suggestion length is 500 characters. Yours is " 
            + suggestContents.length());
            MessageUtils.sendMessage(msg.getChannel().getId(),em.build(),15);
            msg.delete().queue();
            return;
        }

        String sb = suggestContents;
        String timeStamp = new SimpleDateFormat("yyyy.MM.dd HH:mm:ss").format(new Date());
        if (Util.memberHasPermission(msg.getMember(),Permission.NONE)) {
            User devel = Bot.getInstance().shards.getUserById(Bot.getInstance().getConfig().getbotDeveloperId());
            //debug
            //System.out.println(devel);
            //System.out.println(suggestContents);
            //System.out.println(timeStamp);

            // first opens channel to developer then sends success message to channel
            em.setTitle("Suggestions", null)
            .setColor(Color.CYAN)
            .addField("User: ",msg.getAuthor().getName(),false)
            .addField("Server: ",msg.getGuild().getName(),false)
            .addField("Report","\"" + sb + " \"", false)
            .setFooter("Message was sent Local time " + timeStamp, null);
            MessageUtils.sendPrivateMessage(devel.getId(),em.build());
            MessageUtils.sendPrivateMessage(msg.getAuthor().getId(),em.build());
            em.clearFields();
            em.setTitle("Success", null)
            .setColor(Util.resolveColor(Util.memberFromMessage(msg), Color.GREEN))
            .setDescription("Your suggestion has been sent!")
            .addField("Github: ",Bot.REPO, true);
            MessageUtils.sendMessage(msg.getChannel().getId(),em.build(),15);
            msg.delete().queue();
        } else{
            em.setTitle("Suggestion Failed", null)
            .setColor(Util.resolveColor(Util.memberFromMessage(msg), Color.RED))
            .setDescription("Your suggestion cannot be sent unless you have higher permissions!\n Check out the github.")
            .addField("Github: ",Bot.REPO, true);
            MessageUtils.sendMessage(msg.getChannel().getId(),em.build(),15);
            msg.delete().queue();
        }
    }
}