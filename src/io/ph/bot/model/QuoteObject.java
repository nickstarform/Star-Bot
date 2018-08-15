package io.ph.bot.model;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.LocalDate;
import java.time.ZoneId;
import java.util.ArrayList;
import java.lang.*;
import java.util.Random;
import java.util.Date;

import io.ph.bot.Bot;
import io.ph.db.ConnectionPool;
import io.ph.db.SQLUtils;
import io.ph.util.Util;
import net.dv8tion.jda.core.entities.Member;

public class QuoteObject {
    private int uniq;
    private LocalDate date;
    private String quoteContent;
    private int hits;
    private String userID;
    private String guildID;

    /**
     * Constructor for QuoteObject
     * @param uniq Unique num of Quote
     * @param quoteContent Contents of Quote
     * @param hits Hits of Quote (set to 0 when creating a new Quote)
     * @param userID userID of creator
     * @param guildID guildID of the guild this was created in
     * @param date date added
     */
    /*
    sqlite> .open Quotes.db
    sqlite> CREATE TABLE discord_quote (
       ...> uniq integer PRIMARY KEY autoincrement,
       ...> quoteContent text NOT NULL,
       ...> hits integer NOT NULL,
       ...> userID text NOT NULL,
       ...> guildID text NOT NULL,
       ...> date text NOT NULL
       ...> );
    sqlite> .quit
    */
    public QuoteObject(int uniq, String quoteContent, int hits,
            String userID, String guildID) {
        this.uniq = uniq;
        this.date = LocalDate.now(ZoneId.of("America/New_York"));
        this.quoteContent = quoteContent;
        this.hits = hits;
        this.userID = userID;
        this.guildID = guildID;
    }

    public QuoteObject(int uniq, String quoteContent, int hits,
            String userID, String guildID, LocalDate date) {
        this.date = date;
        this.uniq = uniq;
        this.quoteContent = quoteContent;
        this.hits = hits;
        this.userID = userID;
        this.guildID = guildID;
    }
    public static QuoteObject forName(int uniq, String guildID) throws IllegalArgumentException {
        return forName(uniq, guildID, false);
    }

    /**
     * Returns top Quote and hits
     * @param guildID
     * @return Object array with index uniq, date_created,quoteContent, hits, userID
     * @throws NoMacroFoundException
     */
    public static QuoteObject topQuote(String guildID) throws IllegalArgumentException {
        Connection conn = null;
        PreparedStatement stmt = null;
        ResultSet rs = null;
        try {
            conn = ConnectionPool.getConnectionQuote(guildID);
            stmt = conn.prepareStatement("SELECT uniq, date,quoteContent, hits, userID FROM `discord_quote` ORDER BY hits DESC LIMIT 1");
            rs = stmt.executeQuery();
            if(!rs.isBeforeFirst())
                return null;
            rs.next();
            return new QuoteObject(rs.getInt(1), rs.getString(3), rs.getInt(4), rs.getString(5),guildID, LocalDate.parse(rs.getString(2)));
        } catch(SQLException e) {
            e.printStackTrace();
        } finally {
            SQLUtils.closeQuietly(rs);
            SQLUtils.closeQuietly(stmt);
            SQLUtils.closeQuietly(conn);
        }
        return null;
    }

    /**
     * Get and return a Quote for given quoteName
     * If found, increment the hits
     * @param uniq Quote name to search for
     * @param guildID Guild ID to search in
     * @return uniq if found
     * @throws NoMacroFoundException if no Quote is found
     */
    public static QuoteObject forName(int uniq, String guildID, boolean hit) throws IllegalArgumentException {
        Connection conn = null;
        PreparedStatement stmt = null;
        ResultSet rs = null;
        try {
            conn = ConnectionPool.getConnectionQuote(guildID);
            // QuoteObject(int uniq, String quoteContent, int hits, String userID, String guildID, LocalDate date)
            String sql = "SELECT * FROM `discord_quote` WHERE uniq = ?";
            stmt = conn.prepareStatement(sql);
            stmt.setInt(1, uniq);
            rs = stmt.executeQuery();
            if(!rs.isBeforeFirst()) {
                throw new IllegalArgumentException("No Quote found for user: " + rs.getString(4) + " and #"+ uniq);
            }
            rs.next();
            if(hit) {
                sql = "UPDATE `discord_quote` SET hits = hits+1 WHERE uniq = ?";
                PreparedStatement stmt2 = conn.prepareStatement(sql);
                stmt2.setInt(1, uniq);
                stmt2.execute();
                SQLUtils.closeQuietly(stmt2);
            }
            // QuoteObject(int uniq, String quoteContent, int hits, String userID, String guildID, LocalDate date)
            return new QuoteObject(rs.getInt(1), rs.getString(2), rs.getInt(3), rs.getString(4),
                    guildID, LocalDate.parse(rs.getString(6)));
        } catch(SQLException e) {
            e.printStackTrace();
        } finally {
            SQLUtils.closeQuietly(rs);
            SQLUtils.closeQuietly(stmt);
            SQLUtils.closeQuietly(conn);
        }
        return null;
    }

    /**
     * Delete a Quote that is in the database
     * @param requesterId The user that is requesting the delete
     * @return True if deleted, false if user doesn't have permissions
     * Prerequisite: Quote is in the database
     */
    public boolean delete(String requesterId) {
        Connection conn = null;
        PreparedStatement stmt = null;
        ResultSet rs = null;
        try {
            String sql;
            conn = ConnectionPool.getConnectionQuote(this.guildID);
            Member m = Bot.getInstance().shards.getGuildById(this.guildID).getMemberById(requesterId);
            //If user isn't a mod, need to check that they made this
            if (!Util.memberHasPermission(m, Permission.KICK)) {
                sql = "SELECT hits FROM `discord_quote` WHERE uniq = ? AND userID = ?";
                stmt = conn.prepareStatement(sql);
                stmt.setInt(1, this.uniq);
                stmt.setString(2, requesterId);
                try {
                    rs = stmt.executeQuery();
                    if(!rs.isBeforeFirst())
                        return false;
                } catch(SQLException e) {
                    e.printStackTrace();
                } finally {
                    SQLUtils.closeQuietly(rs);
                    SQLUtils.closeQuietly(stmt);
                }
            }

            sql = "DELETE FROM `discord_quote` WHERE uniq = ? AND userID = ?";
            stmt = conn.prepareStatement(sql);
            stmt.setInt(1, this.uniq);
            stmt.setString(2, this.userID);
            stmt.execute();
            return true;
        } catch(SQLException e) {
            e.printStackTrace();
            return false;
        } finally {
            SQLUtils.closeQuietly(rs);
            SQLUtils.closeQuietly(stmt);
            SQLUtils.closeQuietly(conn);
        }
    }

    /**
     * Edit a Quote that is in the database
     * @param requesterId The user that is requesting the edit
     * @return True if deleted, false if user doesn't have permissions
     * Prerequisite: Quote is in the database
     */
    public boolean edit(String requesterId, String newContent, String userID) {
        Connection conn = null;
        PreparedStatement stmt = null;
        ResultSet rs = null;
        try {
            String sql;
            conn = ConnectionPool.getConnectionQuote(this.guildID);
            Member m = Util.resolveUserFromMessage(requesterId,this.guildID);
            //If user isn't a mod, need to check that they made this
            if (!Util.memberHasPermission(m, Permission.KICK)) {
                sql = "SELECT hits FROM `discord_quote` WHERE uniq = ? AND userID = ?";
                stmt = conn.prepareStatement(sql);
                stmt.setInt(1, this.uniq);
                stmt.setString(2, requesterId);
                try {
                    rs = stmt.executeQuery();
                    if(!rs.isBeforeFirst())
                        return false;
                } catch(SQLException e) {
                    e.printStackTrace();
                } finally {
                    SQLUtils.closeQuietly(rs);
                    SQLUtils.closeQuietly(stmt);
                }
            }

            sql = "UPDATE `discord_quote` SET quoteContent=?,userID=? WHERE uniq = ?";
            stmt = conn.prepareStatement(sql);
            stmt.setString(1, newContent);
            stmt.setString(2, userID);
            stmt.setInt(3, this.uniq);
            stmt.execute();
            return true;
        } catch(SQLException e) {
            e.printStackTrace();
            return false;
        } finally {
            SQLUtils.closeQuietly(rs);
            SQLUtils.closeQuietly(stmt);
            SQLUtils.closeQuietly(conn);
        }
    }

    /**
     * Finalize this Quote and insert it into the database
     * @return True if successful, false if key conflict
     * @throws SQLException  Something broke - check stacktrace
     */
    public String create() throws SQLException {
        Connection conn = null;
        PreparedStatement stmt = null; 
        ResultSet getGeneratedKeys = null;

        try {
            // int uniq, String quoteContent, int hits, String userID, String guildID, LocalDate date)
            conn = ConnectionPool.getConnectionQuote(this.guildID);
            String sql = "INSERT INTO `discord_quote` (quoteContent, hits, userID, guildID, date) VALUES (?,?,?,?,?)";
            stmt = conn.prepareStatement(sql);
            stmt.setString(1, this.quoteContent);
            stmt.setInt(2, 0);
            stmt.setString(3, this.userID);
            stmt.setString(4, this.guildID);
            stmt.setString(5, this.date.toString());
            stmt.execute();
            getGeneratedKeys = conn.prepareStatement("SELECT last_insert_rowid()").executeQuery();
            String newuniq = getGeneratedKeys.getString(1);
            return newuniq;

        } catch(SQLException e) {
            if(e.getErrorCode() == 19) {
                return "";
            }
            throw e;
        } finally {
            SQLUtils.closeQuietly(stmt);
            SQLUtils.closeQuietly(conn);
        }
    }

    /**
     * Geta random unique quote from the guild
     * @param guildID guildID to search in
     * @return Null if no results, string of random Quote name if true
     */
    public static int chooseGuildQuotesUniq(String guildID) {

        Random randomGenerator;
        Connection conn = null;
        PreparedStatement stmt = null;
        ResultSet rs = null;
        int size = 0;
        ArrayList<String> toReturn = new ArrayList<String>(4);

        try {
            conn = ConnectionPool.getConnectionQuote(guildID);
            String sql = "SELECT uniq FROM `discord_quote`";
            stmt = conn.prepareStatement(sql);
            // int uniq, String quoteContent, int hits, String userID, String guildID, LocalDate date)
            rs = stmt.executeQuery();
            if(!rs.isBeforeFirst()) {
                throw new IllegalArgumentException("Error in case choosing random quote");
            }
            while (rs.next()){
                size++;
                toReturn.add(Integer.toString(rs.getInt(1)));
            }
            randomGenerator = new Random();
            int index = randomGenerator.nextInt(size);
            return Integer.parseInt(toReturn.toArray(new String[0])[index]);
        } catch(SQLException e) {
            e.printStackTrace();
            return 0;
        } finally {
            SQLUtils.closeQuietly(rs);
            SQLUtils.closeQuietly(stmt);
            SQLUtils.closeQuietly(conn);
        }
    }

    /**
     * This is the main function for getting a random quote
     * @param guildID guildID to search in
     * @return Null if no results, QuoteObject if found
     */
    public static QuoteObject chooseRandomQuote(String guildID) {
        
        int uniq = chooseGuildQuotesUniq(guildID);

        return forName(uniq,guildID,true);
    }

    /**
     * Search for Quotes by user and given guild
     * @param userID userID to search for
     * @param guildID guildID to search in
     * @return Null if no results, populated string array of Quote names if results
     */
    public static String[] searchByUser(String userID, String guildID) {
        Connection conn = null;
        PreparedStatement stmt = null;
        ResultSet rs = null;
        ArrayList<String> toReturn = new ArrayList<String>(1);
        try {
            conn = ConnectionPool.getConnectionQuote(guildID);
            String sql = "SELECT uniq FROM `discord_quote` WHERE userID = ?";
            stmt = conn.prepareStatement(sql);
            stmt.setString(1, userID);
            rs = stmt.executeQuery();
            if(!rs.isBeforeFirst())
                return null;
            while(rs.next()) {
                toReturn.add(Integer.toString(rs.getInt(1)));
            }
            return toReturn.toArray(new String[0]);
        } catch(SQLException e) {
            e.printStackTrace();
            return null;
        } finally {
            SQLUtils.closeQuietly(rs);
            SQLUtils.closeQuietly(stmt);
            SQLUtils.closeQuietly(conn);
        }
    }

    public LocalDate getDate() {
        return date;
    }

    public int getQuoteUniq() {
        return uniq;
    }

    public String getQuoteContent() {
        return quoteContent;
    }

    public int getHits() {
        return hits;
    }

    public String getUserID() {
        return userID;
    }
    public Member getFallbackUsername() {
        return Util.resolveUserFromMessage(userID, guildID); // returns member
    }

    public String getGuildID() {
        return guildID;
    }
}
