# run with PYTHONPATH=/usr/share/anki (i)python2

---

# remove reverse cards

from anki.storage import Collection

col = Collection('/home/rafal/Documents/Anki/Rafal/collection.anki2')

print 'Bulk-deleting reverse cards.'
#did = col.decks.byName('Deutsch')['id']
#col.db.execute('delete from cards where did=:did and ord=1', did=did)
col.db.execute('delete from cards where ord=1')
col.db.commit()

for noteId in col.findNotes(''):
    note = col.getNote(noteId)
    print 'Processing noteId=%(noteId)d, front=\'%(front)s\'' % {'noteId': noteId, 'front': note['Front']}
    note['Add Reverse'] = ''
    note.flush()

col.close()

---

# add reverse card with scheduling information of the forward card
# the usual way would schedule it as new

from anki.storage import Collection
from anki.utils import timestampID

col = Collection('/home/rafal/Documents/Anki/Rafal/collection.anki2')

#did = col.decks.byName('Deutsch')['id']
#noteIdsWithReverse = set([id for id, in col.db.all('select distinct nid from cards where did=:did and ord=1', did=did)])
noteIdsWithReverse = set([id for id, in col.db.all('select distinct nid from cards where ord=1')])

for row in [list(r) for r in col.db.execute('''
                                            select id, nid, did, ord, mod, usn,
                                                   type, queue, due, ivl, factor, reps,
                                                   lapses, left, odue, odid, flags, data
                                            from cards where ord=0
                                            order by id
                                            ''')]:
    note = col.getNote(row[1])
    print 'Processing noteId=%(noteId)d, front=\'%(front)s\'' % {'noteId': note.id, 'front': note['Front']}
    if note.id in noteIdsWithReverse:
        print '  Not adding reverse as it already has it.'
        continue
    row[0] = timestampID(col.db, 'cards') # id
    row[3] = 1 # ord
    row[5] = col.usn()
    col.db.execute('''
                   insert into cards(id, nid, did, ord, mod, usn,
                                     type, queue, due, ivl, factor, reps,
                                     lapses, left, odue, odid, flags, data)
                              values(''' + ','.join(len(row) * ['?']) + ''')
                   ''', *row)
    # set reverse now, after the card was added - prevents generating the new card automatically
    note['Add Reverse'] = 'y'
    note.flush()

col.close()

---

# create a new note with a single card

from anki.storage import Collection

col = Collection('/home/rafal/Documents/Anki/Rafal/collection.anki2')

#col.models.allNames()
col.models.setCurrent(col.models.byName(u'Español'))
note = col.newNote()
note['Front'] = 'dupa'
note['Back'] = 'el culo'
col.addNote(note)
col.save()

# update the note by adding the reverse card

note['Add Reverse'] = 'y'
note.flush()

col.close()

---

# review day percentage calculation reverse engineering
# result: Anki takes the first ever day of review as a number of how many days
# ago it was and total number of days with reviews and uses that
# this means days without any scheduled review will influence the stats, not
# sure if this is good
# to fake a review for a day just move from other day a review in the revlog
# table - set the id to the timestamp in millis of the faked day

from anki.storage import Collection
import types

col = Collection('/Users/rafal/Playground/collection.anki2')
did = col.decks.byName('Español')['id']
col.decks.select(did)

stats = col.stats()
stats.type = 2 # lifetime

def daysStudiedSql(self):
    # copied from _daysStudied to just show the SQL, not execute it
    lims = []
    num = self._periodDays()
    if num:
        lims.append(
            "id > %d" % ((self.col.sched.dayCutoff-(num*86400))*1000))
    rlim = self._revlogLimit()
    if rlim:
        lims.append(rlim)
    if lims:
        lim = "where " + " and ".join(lims)
    else:
        lim = ""
    return "select count(), abs(min(day)) from (select (cast((id/1000 - {cut}) / 86400.0 as int)+1) as day from revlog {lim} group by day order by day)".format(lim=lim, cut=self.col.sched.dayCutoff)

stats._daysStudiedSql = types.MethodType(daysStudiedSql, stats)
stats._daysStudiedSql()
period = stats._deckAge('review')
(daysStud, fstDay) = stats._daysStudied()
daysStud, fstDay, period

"%(pct)d%% (%(x)s of %(y)s)" % dict(x=daysStud, y=period, pct=daysStud/float(period)*100)

col.close()

# col.crt is creation timestamp
# sched.today is day number after creation
# sched.dayCutoff is end of current day

# select id from cards where did in (1435088749676)
# - returns all cards for deck Español

# select * from revlog where cid in (select id from cards where did in (1435088749676))
# - returns all reviews on all days for all cards for deck Español

# revlog.id is time.time() of review * 1000 (millis)

# select (cast((id/1000 - 1534543200 # cutoff #) / 86400.0 as int)+1) as day from revlog where cid in
#     (select id from cards where did in (1435088749676))
# - returns all days with reviews for all cards for deck Español
# - days 1 for today, 0 for yesterday, negative for more past days

# select (cast((id/1000 - 1534543200 # cutoff #) / 86400.0 as int)+1) as day from revlog where cid in
#     (select id from cards where did in (1435088749676))
# group by day order by day
# - returns distinct days with reviews for all cards for deck Español
# - days 1 for today, 0 for yesterday, negative for more past days

# select count(), abs(min(day)) from
#     (select (cast((id/1000 - 1534543200 # cut #) / 86400.0 as int)+1) as day from revlog where cid in
#         (select id from cards where did in (1435088749676))
#     group by day order by day)
# - returns count of all days with any reviews and how many days ago the first review was done (when reviewing started)
