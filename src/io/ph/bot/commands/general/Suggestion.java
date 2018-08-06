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
import net.dv8tion.jda.core.EmbedBuilder;
import net.dv8tion.jda.core.entities.Member;
import net.dv8tion.jda.core.entities.Message;
import net.dv8tion.jda.core.entities.Role;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.temporal.ChronoUnit;
import java.util.Date;
import java.text.SimpleDateFormat;
/**
 * Send suggestion to creator
 * @author Nick
 */
@CommandData (
        defaultSyntax = "suggestion",
        aliases = {"suggest","suggestions"},
        category = CommandCategory.UTILITY,
        permission = Permission.KICK,
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
            .setDescription("Maximum suggestion length is 500 characters. Yours is " 
            + suggestContents.length());
            msg.getChannel().sendMessage(em.build()).queue();
            return;
        }

        String sb = suggestContents;
        String timeStamp = new SimpleDateFormat("yyyy.MM.dd HH:mm:ss").format(new Date());

        String devel = Bot.getInstance().getBots().get(0).getUserById(Long.toString(Bot.getInstance().getConfig().getbotDeveloperId())).getName();

        Util.resolveMemberFromMessage(devel,msg.getGuild()).getUser().openPrivateChannel().queue(success -> {
            em.setTitle("Suggestions", null)
            .setColor(Color.CYAN)
            .addField("User: ",Util.resolveMemberFromMessage(msg).getUser().getName(),false)
            .addField("Server: ",msg.getGuild().getName(),false)
            .addField("",sb + " \"", false)
            .setFooter("Message was sent Local time " + timeStamp, null);
            Util.resolveMemberFromMessage(msg).getUser().openPrivateChannel().complete()
            .sendMessage(em.build()).queue(success1 -> {
                em.clearFields();
                em.setTitle("Success", null)
                .setColor(Util.resolveColor(Util.memberFromMessage(msg), Color.GREEN))
                .setDescription("Your suggestion has been sent!");
                msg.getChannel().sendMessage(em.build()).queue();
            });
        });
    }
}