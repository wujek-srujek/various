#!/usr/bin/env python3

import os
from collections import defaultdict

src = '/Users/rswierzy/Pictures_3_3'

def list_strange():
  ext2file = defaultdict(list)

  for root, dirs, files in os.walk(src):
    for f in files:
      path = os.path.join(root, f)
      name, ext = os.path.splitext(f)
      if ext.lower() in {'.jpg', '.jpeg', '.mov','.mp4', '.wmv', '.mpg', '.pdf'}:
        continue
      if ext:
        ext2file[ext].append(path)
      else:
        ext2file['EXTONLY'].append(path)

  for ext, files in ext2file.items():
    print(ext, len(files))
    for f in files:
      print('    ', f)

def stats():
  for root, dirs, files in os.walk(src):
    print('{:40} {} dirs    {} files'.format(os.path.relpath(root, src), len(dirs), len(files)))

def delete_strange():
  for root, dirs, files in os.walk(src):
    for f in files:
      name, ext = os.path.splitext(f)
      if ext.lower() not in {'.jpg', '.jpeg', '.mov','.mp4', '.wmv', '.mpg', '.pdf'}:
        os.remove(os.path.join(root, f))

def fix_spaces():
  for root, dirs, files in os.walk(src):
    for f in files:
      os.rename(os.path.join(root, f), os.path.join(root, f.replace(' ', '_')))

    for i in range(len(dirs)):
      new_name = dirs[i].replace(' ', '_')
      os.rename(os.path.join(root, dirs[i]), os.path.join(root, new_name))
      dirs[i] = new_name

def move_other():
  for root, dirs, files in os.walk(src):
    for f in files:
      name, ext = os.path.splitext(f)
      if ext.lower() in {'.mov','.mp4', '.wmv', '.mpg', '.pdf'}:
        relpath = os.path.relpath(root, src)
        dst = os.path.join('/Users/rswierzy/Movies', relpath)
        os.makedirs(dst, exist_ok=True)
        os.rename(os.path.join(root, f), os.path.join(dst, f))
        

#fix_spaces()
list_strange()
#stats()
#delete_strange()
#move_other()
