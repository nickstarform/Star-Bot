package io.ph.util;

import java.awt.Color;

import io.ph.bot.Bot;
import io.ph.bot.commands.Command;
import io.ph.bot.model.GuildObject;
import net.dv8tion.jda.api.EmbedBuilder;
import net.dv8tion.jda.api.entities.Message;
import net.dv8tion.jda.api.entities.TextChannel;
import net.dv8tion.jda.api.entities.MessageEmbed;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;
import io.ph.util.Util;

public class MessageUtils {
    /**
     * Send a message embed to a channel
     * @param channelId Channel ID
     * @param e MessageEmbed
     */
    public static void sendMessage(String channelId, MessageEmbed e) {
        sendMessage(channelId,e,-1);
    }
    
    /**
     * Send a message to a channel
     * @param channelId Channel ID
     * @param msg String of message
     */
    public static void sendMessage(String channelId, String msg) {
        sendMessage(channelId,msg,-1);
    }

    /**
     * Send a message embed to a channel and deletes after some time
     * @param channelId Channel ID
     * @param e MessageEmbed
     * @param delete Integer of # seconds to wait before deleting message
     */
    public static void sendMessage(String channelId, MessageEmbed e, 
                                   int delete) {

        String botIDlong = Bot.getInstance().getConfig().getBotInviteBotLink().split("\\=")[1].split("\\&")[0];
        TextChannel textChannel = Bot.getInstance().shards.getTextChannelById(channelId);

        if (delete == -1) {
            textChannel.sendMessage(e).queue();
        } else {
            Message tM = textChannel.sendMessage(e).complete();
            try {
                Thread.sleep(1000*delete);
                textChannel.deleteMessageById(tM.getId()).queue();
            } catch(InterruptedException ex) {
                Thread.currentThread().interrupt();
            }
        }
    }
    
    /**
     * Send a message to a channel
     * @param channelId Channel ID
     * @param msg String of message
     * @param delete Integer of # seconds to wait before deleting message
     */
    public static void sendMessage(String channelId, String msg, 
                                   int delete) {

        String botIDlong = Bot.getInstance().getConfig().getBotInviteBotLink().split("\\=")[1].split("\\&")[0]; 
        TextChannel textChannel = Bot.getInstance().shards.getTextChannelById(channelId);  

        if (delete == -1) {
            textChannel.sendMessage(msg).queue();
        } else {
            Message tM = textChannel.sendMessage(msg).complete();
            try {
                Thread.sleep(1000*delete);
                textChannel.deleteMessageById(tM.getId()).queue();
            } catch(InterruptedException ex) {
                Thread.currentThread().interrupt();
            }
        }
    }

    /**
     * Send a PM to a user
     * @param userId User ID
     * @param msg String of message
     */
    public static void sendPrivateMessage(String userId, String msg) {
        Bot.getInstance().shards.getUserById(userId).openPrivateChannel().queue(ch -> ch.sendMessage(msg).queue(success -> {}, failure -> {
                System.out.println("failed");
                return;
            }));
    }    
    /**
     * Send a PM to a user
     * @param userId User ID
     * @param msg String of message
     */
    public static void sendPrivateMessage(String userId, MessageEmbed msg) {
        Bot.getInstance().shards.getUserById(userId).openPrivateChannel().queue(ch -> ch.sendMessage(msg).queue(success -> {}, failure -> {
                System.out.println("failed");
                return;
            }));
    }
    
    /**
     * Send an error message to a channel when a command is used incorrectly
     * @param msg Original message. This determines which channel to send to
     * @param commandName Name of the command
     * @param args Arguments for the command
     * @param argExplanations Explanations for arguments or command. Each is delimited with a newline
     * @deprecated
     */
    @Deprecated
    public static void badCommandUsage(Message msg, String commandName, String args, String... argExplanations) {
        String prefix = GuildObject.guildMap.get(msg.getGuild().getId()).getConfig().getCommandPrefix();
        EmbedBuilder em = new EmbedBuilder();
        em.setTitle(String.format("%s usage", prefix + commandName), null)
        .setColor(Color.RED)
        .appendDescription(String.format("%s%s %s\n", prefix, commandName, args));
        
    }
    
    /**
     * Generic error message for misuse of command
     * @param msg Message in which command was used incorrectly
     * @param cmd Instance of command that was used incorrectly
     */
    public static void sendIncorrectCommandUsage(Message msg, Command cmd) {
        EmbedBuilder em = new EmbedBuilder();
        em.setTitle("Incorrect usage", null)
        .setColor(Color.RED)
        .setDescription(String.format("Incorrect command usage. For more info, use %shelp %s",
                GuildObject.guildMap.get(msg.getGuild().getId()).getConfig().getCommandPrefix(), 
                cmd.getDefaultCommand()));
        sendMessage(msg.getChannel().getId(),em.build(),10);
    }
    
    /**
     * Generic response to failure in restaction
     * @param throwable Throwable failure
     * @return MessageEmbed formatted correctly
     */
    public static MessageEmbed handleFailure(Throwable throwable) {
        EmbedBuilder em = new EmbedBuilder();
        em.setTitle("Error", null)
        .setColor(Color.RED)
        .setDescription(throwable.getMessage());
        return em.build();
    }

    /**
     * This helps to split up the quotes just incase there are an excessive amount. 
     * @param totalString ArrayList of messages to send. Will stagger the message 
     * @param msg Message object for communications
     * @param em Embedded Builder
     */
    public static void staggerArray(ArrayList<String> totalString,
                                     Message msg,
                                     EmbedBuilder em) {
        staggerArray(totalString,msg,em,null);
    }

    /**
     * This helps to split up the quotes just incase there are an excessive amount. 
     * @param totalString ArrayList of messages to send. Will stagger the message 
     * @param msg Message object for communications
     * @param em Embedded Builder
     * @param cEm Embedded Builder forced color
     */
    public static void staggerArray(ArrayList<String> totalString,
                                     Message msg,
                                     EmbedBuilder em,
                                     Color cEm) {
        AtomicInteger index = new AtomicInteger(0);
        ArrayList<String> temp = new ArrayList<String>(1);
        for (int i = 0; i < totalString.size(); i++) {
            String field = totalString.get(i).toString();
            // debug
            //System.out.println("Index: " + index.toString() + "/" + totalString.size());
            //System.out.println("Field: " + field);
            if ((index.get() < 35) && (i != totalString.size() - 1)) {
                temp.add(field + "\n");
                index.incrementAndGet();
            } else {
                em.setColor(Util.resolveColor(Util.memberFromMessage(msg), Color.GREEN,cEm));
                temp.add(field + "\n");
                // debug
                //String tempB = Util.combineStringArray(temp);
                //System.out.println("Field: " + tempB);
                em.setDescription(Util.combineStringArray(temp));
                sendMessage(msg.getChannel().getId(),em.build());
                em.clearFields();
                temp.clear();  
                index.set(0);
            }
        }  
    }  
}
