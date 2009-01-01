"""
OpenLP - Open Source Lyrics Projection
Copyright (c) 2008 Raoul Snyman
Portions copyright (c) 2008 Martin Thompson, Tim Bentley

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; version 2 of the License.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program; if not, write to the Free Software Foundation, Inc., 59 Temple
Place, Suite 330, Boston, MA 02111-1307 USA
"""
import os 
import logging
import sqlite3
from openlp.core.lib import PluginConfig

class MigrateSongs():
    def __init__(self, display):
        self.display = display
        self.config = PluginConfig("Songs")
        self.data_path = self.config.get_data_path()     
        self.database_files = self.config.get_files("olp3")

    def process(self):
        self.display.output("Songs processing started");
        for f in self.database_files:
            self.v_1_9_0(f)
        self.display.output("Songs processing finished");          

    def v_1_9_0(self, database):
        self.display.output("Migration 1.9.0 Started for "+database);
        self._v1_9_0_authors(database)
        self._v1_9_0_topics(database)      
        self._v1_9_0_songbook(database) 
        
        conn = sqlite3.connect(self.data_path+"/"+database)
        conn.text_factory = str        
        c = conn.cursor()
        #cmd = "sqlite3 -echo "+ self.data_path+"/"+database + ' "create index if not exists sa1121 on songauthors (authorid ASC,songid ASC) ;"'
        #print cmd
        #f_i, f_o  = os.popen4(cmd)
        #out = f_o.readlines()
        #print out
        #self.display.output(f_o.readlines())
        c.execute("""select * from songs where songtitle like '%Come now%'""")        

        conn.commit()
        #self.display.sub_output("Index SA1 created " + database);          
        #c.execute("""create index if not exists sa2 on songauthors (songid ASC,authorid ASC) """)        
        #conn.commit()
        #self.display.sub_output("Index SA2 created " + database);          
        conn.close()
        self.display.output("Migration 1.9.0 Finished for " + database);            

    def _v1_9_0_authors(self, database):
        self.display.sub_output("Authors Started for "+database); 
        cmd = "sqlite3 -echo "+ self.data_path+"/"+database + ' "alter table authors add column first_name varchar(40);"'
        self.run_cmd(cmd)
        self.display.sub_output("first name created")
        cmd = "sqlite3 -echo "+ self.data_path+"/"+database + ' "alter table authors add column last_name varchar(40);"'
        self.run_cmd(cmd)        
        self.display.sub_output("last name created")
        cmd = "sqlite3 -echo "+ self.data_path+"/"+database + ' "create index if not exists author1 on authors (authorname ASC,authorid ASC);"'
        self.run_cmd(cmd)        
        self.display.sub_output("index author1 created")
        cmd = "sqlite3 -echo "+ self.data_path+"/"+database + ' "create index if not exists author2 on authors (last_name ASC,authorid ASC);"'
        self.run_cmd(cmd)        
        self.display.sub_output("index author2 created")
        cmd = "sqlite3 -echo "+ self.data_path+"/"+database + ' "create index if not exists author3 on authors (first_name ASC,authorid ASC);"'
        self.run_cmd(cmd)        
        self.display.sub_output("index author3 created")           
        self.display.sub_output("Authors Completed");
        
    def _v1_9_0_topics(self, database):
        self.display.sub_output("Topics Started for "+database); 
        cmd = "sqlite3 -echo "+ self.data_path+"/"+database + ' "create table if not exists topics (topic_id integer Primary Key ASC AUTOINCREMENT);"'
        self.run_cmd(cmd)
        self.display.sub_output("Topic table created")
        cmd = "sqlite3 -echo "+ self.data_path+"/"+database + ' "alter table topics add column topic_name varchar(40);"'
        self.run_cmd(cmd) 
        self.display.sub_output("topicname added")        
        cmd = "sqlite3 -echo "+ self.data_path+"/"+database + ' "create index if not exists topic1 on topics (topic_name ASC,topic_id ASC);"'
        self.run_cmd(cmd)        
        self.display.sub_output("index topic1 created")           
        
        self.display.sub_output("Topics Completed");
        
    def _v1_9_0_songbook(self, database):
        self.display.sub_output("SongBook Started for "+database); 
        cmd = "sqlite3 -echo "+ self.data_path+"/"+database + ' "create table if not exists songbook (songbook_id integer Primary Key ASC AUTOINCREMENT);"'
        self.run_cmd(cmd)
        self.display.sub_output("SongBook table created")
        cmd = "sqlite3 -echo "+ self.data_path+"/"+database + ' "alter table songbook add column songbook_name varchar(40);"'
        self.run_cmd(cmd) 
        self.display.sub_output("songbook_name added")
        cmd = "sqlite3 -echo "+ self.data_path+"/"+database + ' "alter table songbook add column songbook_publisher varchar(40);"'
        self.run_cmd(cmd) 
        self.display.sub_output("songbook_publisher added")  
        cmd = "sqlite3 -echo "+ self.data_path+"/"+database + ' "create index if not exists songbook1 on songbook (songbook_name ASC,songbook_id ASC);"'
        self.run_cmd(cmd)        
        self.display.sub_output("index songbook1 created")         
        cmd = "sqlite3 -echo "+ self.data_path+"/"+database + ' "create index if not exists songbook2 on songbook (songbook_publisher ASC,songbook_id ASC);"'
        self.run_cmd(cmd)        
        self.display.sub_output("index songbook2 created")            
        self.display.sub_output("SongBook Completed");
        
        
    def run_cmd(self, cmd):
        f_i, f_o  = os.popen4(cmd)
        out = f_o.readlines()
        if len(out) > 0:
              for o in range (0, len(out)):
                self.display.sub_output(out[o])        
