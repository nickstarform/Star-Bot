package io.ph.bot.commands.general;

import java.awt.Color;
import java.sql.SQLException;
import java.util.Iterator;
import org.apache.commons.lang3.StringUtils;
import java.util.List;
import java.time.LocalDate;
import java.lang.*;

import io.ph.bot.commands.Command;
import io.ph.bot.commands.CommandCategory;
import io.ph.bot.commands.CommandData;
import io.ph.bot.model.GuildObject;
import io.ph.bot.model.QuoteObject;
import io.ph.bot.model.Permission;
import io.ph.util.MessageUtils;
import io.ph.util.Util;
import io.ph.bot.Bot;
import net.dv8tion.jda.core.EmbedBuilder;
import net.dv8tion.jda.core.entities.Member;
import net.dv8tion.jda.core.entities.Message;
import net.dv8tion.jda.core.entities.Guild;

/**
 * Create, delete, search, call information, and call Quotes
 * A quote is a way of remembering the absurdity of a user
 * @author Nick
 *
 */
@CommandData (
        defaultSyntax = "quote",
        aliases = {"quotes","q"},
        category = CommandCategory.FUN,
        permission = Permission.NONE,
        description = "Create, delete, edit, search, or get information on a quote\n"
                + "Quotes are text from user that are saved to a db to be called later",
        example = "create \"QuotedUser\" contents *This creates a quote for user `QuotedUser`*\n"
                + "delete 57 *This deletes the quote 57*\n"
                + "edit \"57\" new contents *This edits the quote #57's contents*\n"
                + "list \"QuotedUser\" *lists all quotes created by the QuotedUser*\n"
                + "showall *lists all quotes for server*\n"
                + "info 57 *This gives information on the quote #57*\n"
                + "top *Will rank the top quofte*\n"
                //+ "rank *Will rank the top 10 quotes*\n"
                + "if no arg will select random quote \n"
        )
public class Quote extends Command {
    private EmbedBuilder em;
    private Message msg;
    private String contents;
    private int uniq;

    @Override
    public void executeCommand(Message msg) {
        this.msg = msg;
        this.em = new EmbedBuilder();
        this.contents = Util.getCommandContents(msg);
        String param = "";
        
        try{
            param = Util.getParam(msg);
        } catch (IndexOutOfBoundsException e) {
            param = "";
        }   
        if(param.equalsIgnoreCase("create")) {
            createQuote();
        } else if(param.equalsIgnoreCase("delete")) {
            deleteQuote();
        } else if(param.equalsIgnoreCase("edit")) {
            editQuote();
        } else if(param.equalsIgnoreCase("list")) {
            listQuotes();
        } else if(param.equalsIgnoreCase("showall")) {
            listQuotesAll();
        } else if (param.equalsIgnoreCase("info")) {
            quoteInfo();
        } else if(param.equalsIgnoreCase("top")) {
            quoteRank();
        //} else if(param.equalsIgnoreCase("rank")) {
        //   quoteRank();
        } else if(!contents.equals("")){
                QuoteObject m = QuoteObject.forName(Integer.parseInt(contents), msg.getGuild().getId().toString(), true);
                msg.getChannel().sendMessage("#" + Integer.toString(m.getQuoteUniq()) 
                    + " \"" + m.getQuoteContent() + "\" ~ " 
                    + m.getFallbackUsername().getUser().getName() 
                    + "#" 
                    + m.getFallbackUsername().getUser().getDiscriminator() 
                    + " on " 
                    + m.getDate().toString()).queue(success -> {msg.delete().queue();});
                return;
        } else {
            // send random quote
            try {
                String[] m = QuoteObject.chooseRandomQuote(msg.getGuild().getId());
                msg.getChannel().sendMessage("#" + m[0] 
                    + " \"" + m[3] + "\" ~ " 
                    + Util.resolveUserFromMessage(m[2], msg.getGuild().getId()).getUser().getName() 
                    + "#" 
                    + Util.resolveUserFromMessage(m[2], msg.getGuild().getId()).getUser().getDiscriminator() 
                    + " on " 
                    + LocalDate.parse(m[1]).toString()).queue(success-> {msg.delete().queue();});
                return;
            } catch (IllegalArgumentException e) {
                em.setTitle("Error", null)
                .setColor(Color.RED)
                .setDescription(e.getMessage());
            }
        }
        // debug
        //System.out.println(param);
        msg.getChannel().sendMessage(em.build()).queue(success -> {msg.delete().queue();});
    }

    /**
     * Create a Quote Object
     */
    private void createQuote() {
        contents = Util.getCommandContents(contents);
        contents = "Nick testing the create quote commands";
        if(contents.equals("") || contents.split(" ").length < 2) {
            em.setTitle("Error", null)
            .setColor(Color.RED)
            .addField(GuildObject.guildMap.get(msg.getGuild().getId()).getConfig().getCommandPrefix() 
                    + "quote create name contents",
                    "You have designated to create a quote, but your"
                            + " command does not meet all requirements\n"
                            + "*name* - Name of the user. If it is multi-worded, "
                            + "you can surround it in \"quotation marks\"\n"
                            + "*contents* - Contents of the quote", true);
            return;
        }
        String[] resolved = resolveQuoteUserAndContents(contents);
        QuoteObject m = new QuoteObject(0, resolved[1], 0, 
            Util.resolveMemberFromMessage(resolved[0],msg.getGuild()).getUser().getId(), 
            msg.getGuild().getId());
        try {
            String ret = m.create();
            if(!ret.equals(null)) {
                em.setTitle("Success", null)
                .setColor(Util.resolveColor(Util.memberFromMessage(msg), Color.GREEN))
                .setDescription("Quote **" + resolved[0] + " #" + ret + "** created");
            } else {
                em.setTitle("Error", null)
                .setColor(Color.RED)
                .setDescription("Weird error. Report to the bot dev with `!suggest`");
            }
        } catch(SQLException e) {
            e.printStackTrace();
        }
    }

    /**
     * Delete a quote
     */
    private void deleteQuote() {
        contents = Util.getCommandContents(contents);
        if(contents.equals("")) {
            em.setTitle("Error", null)
            .setColor(Color.RED)
            .addField(GuildObject.guildMap.get(msg.getGuild().getId()).getConfig().getCommandPrefix() 
                    + "quote delete uniq",
                    "You have designated to delete a quote num, "
                            + "but your command does not meet all requirements\n"
                            + "uniq - Unique ID of the quote.", true);
            return;
        }
        try {
            int i = Integer.parseInt(contents);
            QuoteObject m = QuoteObject.forName(i, msg.getGuild().getId());
            if(m.delete(msg.getAuthor().getId())) {
                em.setTitle("Success", null)
                .setColor(Util.resolveColor(Util.memberFromMessage(msg), Color.GREEN))
                .setDescription("Quote ** #$" + contents + "** deleted");
            } else {
                em.setTitle("Error", null)
                .setColor(Color.RED)
                .setDescription("You cannot delete quote **" + contents + "**")
                .setFooter("Users can only delete their own quotes", null);
            }
        } catch (IllegalArgumentException e) {
            em.setTitle("Error", null)
            .setColor(Color.RED)
            .setDescription(e.getMessage());
        }
    }

    /**
     * Edit a Quote
     */
    private void editQuote() {
        contents = Util.getCommandContents(contents);
        if(contents.equals("")) {
            em.setTitle("Error", null)
            .setColor(Color.RED)
            .addField(GuildObject.guildMap.get(msg.getGuild().getId()).getConfig().getCommandPrefix() 
                    + "quote edit uniq userid,content",
                    "You have designated to edit a quote, but your "
                            + "command does not meet all requirements\n"
                            + "uniq - Name of the quote user.\n"
                            + "content - content of the quote\n"
                            + "userid - userid of the quote", true);
            return;

        }
        String[] resolved = resolveQuoteUserAndContents(contents);
        try {
            int uniq = Integer.parseInt(resolved[0]);
            String userID = Util.resolveMemberFromMessage(resolved[1].split(" ")[0],msg.getGuild()).getUser().getId();
            String newContent = Util.getCommandContents(resolved[1]);
            QuoteObject m = QuoteObject.forName(uniq, msg.getGuild().getId());
            if(m.edit(msg.getAuthor().getId(), newContent,userID)) {
                em.setTitle("Success", null)
                .setColor(Util.resolveColor(Util.memberFromMessage(msg), Color.GREEN))
                .setDescription("Quote **" + uniq + "** edited");
            } else {
                em.setTitle("Error", null)
                .setColor(Color.RED)
                .setDescription("You cannot edit quote **" + uniq + "**")
                .setFooter("Users can only edit their own quotes", null);
            }
        } catch (IllegalArgumentException e) {
            em.setTitle("Error", null)
            .setColor(Color.RED)
            .setDescription("Quote **" + uniq+ "** does not exist");
        }
    }
    
    /**
     * List all quotes made by a user
     */
    private void listQuotes() {
        Member m;
        String possibleUser = Util.getCommandContents(this.contents);
        if (possibleUser.isEmpty()) {
            m = msg.getMember();
        } else {
            m = Util.resolveMemberFromMessage(possibleUser, msg.getGuild());
        }
        String[] results = QuoteObject.searchByUser(m.getUser().getId(), msg.getGuild().getId());
        if (results == null) {
            em.setTitle("Error", null)
            .setColor(Color.RED)
            .setDescription("No quotes found for user " + m.getEffectiveName());
            return;
        }
        StringBuilder sb = new StringBuilder();
        for (String s : results) {
            sb.append(s + ", ");
        }
        
        String finalSb = sb.toString().substring(0, sb.toString().length() - 2);
        
        em.setTitle("Quotes created by " + m.getEffectiveName(), null)
        .setColor(Util.resolveColor(Util.memberFromMessage(msg), Color.GREEN))
        .setDescription(finalSb);
    }

    /**
     * List all quotes made
     */
    private void listQuotesAll() {
        StringBuilder totalString = new StringBuilder();
        List<Member> iteratorion = msg.getGuild().getMembers();
        iteratorion.forEach(j -> {
            String[] results = QuoteObject.searchByUser(j.getUser().getId(),msg.getGuild().getId());
            if (results != null) {
                StringBuilder sb = new StringBuilder();
                for (String s : results) {
                    sb.append(s + ", ");
                }
                String fin = sb.toString();
                totalString.append(j.getUser().getName() + ": " + fin.substring(0, fin.length() - 2) + "\n");
            }
        });
        String finalTotal = totalString.toString();
        em.setTitle("All Quotes created in this guild: ", null)
        .setColor(Util.resolveColor(Util.memberFromMessage(msg), Color.GREEN))
        .setDescription(finalTotal);
    }

    /**
     * Send information on a quote
     */
    private void quoteInfo() {
        contents = Util.getCommandContents(contents);
        if(contents.equals("")) {
            em.setTitle("Error", null)
            .setColor(Color.RED)
            .addField(GuildObject.guildMap.get(msg.getGuild().getId()).getConfig().getCommandPrefix() 
                    + "quote info uniq",
                    "You have designated to search for a quote, "
                            + "but your command does not meet all requirements\n"
                            + "uniq - Unique number quote to display info for.", true);
            return;
        }
        try {
            int uniq = Integer.parseInt(contents);
            QuoteObject m = QuoteObject.forName(uniq, msg.getGuild().getId());
            Member mem = msg.getGuild().getMemberById(m.getUserID());
            em.setTitle("Information on #" + contents, null)
            .setColor(Util.resolveColor(Util.memberFromMessage(msg), Color.GREEN))
            .addField("Creator", m.getFallbackUsername().getUser().getName() + "#" + m.getFallbackUsername().getUser().getDiscriminator(), true)
            .addField("Content", m.getQuoteContent(), true)
            .addField("Hits", m.getHits()+"", true)
            .addField("Date created", m.getDate().toString(), true);
        } catch (IllegalArgumentException e) {
            em.setTitle("Error", null)
            .setColor(Color.RED)
            .setDescription(e.getMessage());
        }
    }

    /**
     * Send information on a quote
     */
    private void quoteInfoShort() {
        contents = Util.getCommandContents(contents);
        if(contents.equals("")) {
            em.setTitle("Error", null)
            .setColor(Color.RED)
            .addField(GuildObject.guildMap.get(msg.getGuild().getId()).getConfig().getCommandPrefix() 
                    + "quote info uniq",
                    "You have designated to search for a quote, "
                            + "but your command does not meet all requirements\n"
                            + "uniq - Unique number quote to display info for.", true);
            return;
        }
        try {
            int uniq = Integer.parseInt(contents);
            QuoteObject m = QuoteObject.forName(uniq, msg.getGuild().getId());
            msg.getChannel().sendMessage("\"" + m.getQuoteContent() + "\" ~ " 
                    + m.getUserID() + " " + m.getDate().toString()).queue(success 
                    -> {msg.delete().queue();});
        } catch (IllegalArgumentException e) {
            em.setTitle("Error", null)
            .setColor(Color.RED)
            .setDescription(e.getMessage());
        }
    }

    /**
     * Send information on a macro
     */
    private void quoteRank() {
        try {
            QuoteObject m = QuoteObject.topQuote(msg.getGuild().getId());
            em.setTitle("Information on #" + Integer. toString(m.getQuoteUniq()), null)
            .setColor(Util.resolveColor(Util.memberFromMessage(msg), Color.GREEN))
            .addField("Creator", m.getFallbackUsername().getUser().getName() + "#" + m.getFallbackUsername().getUser().getDiscriminator(), true)
            .addField("Content", m.getQuoteContent()+"", true)
            .addField("Hits", m.getHits()+"", true)
            .addField("Date created", m.getDate().toString(), true);
        } catch (IllegalArgumentException e) {
            em.setTitle("Error", null)
            .setColor(Color.RED)
            .setDescription(e.getMessage());
        }
    }
    /**
     * Resolve Quote Username and contents from a create statement
     * This works to involve quotations around a spaced quote name
     * @param s The parameters of a create statement - The contents past the $quote create bit
     * @return Multi index array: [0] userid, [1] is the contents
     * Prerequisite: s.split() must have length of >= 2
     */
    private static String[] resolveQuoteUserAndContents(String s) {
        // debug
        //System.out.println(s);
        String[] toReturn = new String[2];
        if(s.contains("\"") && StringUtils.countMatches(s, "\"") > 1) {
            int secondIndexOfQuotes = s.indexOf("\"", s.indexOf("\"") + 1);
            toReturn[0] = s.substring(s.indexOf("\"") + 1, secondIndexOfQuotes);
            toReturn[1] = s.substring(secondIndexOfQuotes + 2);
        } else {
            toReturn[0] = s.split(" ")[0];
            toReturn[1] = Util.getCommandContents(s);
        }
        return toReturn;
    }
}
