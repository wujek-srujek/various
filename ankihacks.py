# run with PYTHONPATH=/usr/share/anki (i)python2

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
