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
import net.dv8tion.jda.core.entities.User;
import java.time.ZoneId;
import java.util.Date;
import java.text.SimpleDateFormat;
import net.dv8tion.jda.core.JDA;
/**
 * Send Report to guild/dev
 * @author Nick
 */
@CommandData (
        defaultSyntax = "report",
        aliases = {},
        category = CommandCategory.UTILITY,
        permission = Permission.NONE,
        description = "Report abuse/harassment/misuse or other wrongdoings of someone or a group of people\n"
                    + "**DO NOT abuse this function**. You will be permanently banned from the bot across all servers.\n"
                    + "Please use the form of the example provided. Please be as descriptive as possible "
                    + "and keep it contained within a single message\n"
                    + "Please be patient and wait for a reply.\n"
                    + "In order to report something you **HAVE** to DM the bot"
                    + "`> report guildId reportContent + pictureAttachment` "
                    + "*(Prefered format, doesn't have to include picture)\n"
                    + "`> report reportContent` "
                    + "*(Basic format, might take longer for conflict resolution)",
        example = ""
        )
public class Report extends Command {

    @Override
    public void executeCommand(Message msg) {
        EmbedBuilder em = new EmbedBuilder();
        em.setTitle("Report Function", null)
        .setColor(Util.resolveColor(Util.memberFromMessage(msg), Color.YELLOW))
        .setDescription("Reports only work in DMs to the bot  <@"
                    + Bot.getInstance().getConfig().getBotInviteBotLink().split("\\=")[1].split("\\&")[0] + ">.\n"
                    + "To view the report form DM the bot with the command `report`." 
                    + "**DO NOT** abuse this function. You will be banned from bot use, permanently and with no repeal.");
        MessageUtils.sendMessage(msg.getChannel().getId(),em.build(),20);
        msg.delete().queue();
    }
}