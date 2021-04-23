import threading
import timeit

def send_file(old, new, t):

  # write log in log.txt(start)
  start_time = timeit.default_timer()-start_program
  start_log = '{0:<8.2f}Start copying {1} to {2}\n'.format(start_time, old_file,new_file)
  lock.acquire()
  log_file = open('log.txt', 'at')
  log_file.write(start_log)
  log_file.close()
  lock.release()

  # read old file and write to new file 
  read_file = open(old, 'rb')
  write_file = open(new, 'wb')
  # read file 10Kbytes
  while (byte := read_file.read(10240)):
    write_file.write(byte)
  read_file.close()
  write_file.close()
  
  #write log in log.txt(finish)
  finish_time = timeit.default_timer()
  finish_log= '{0:<8.2f}{1} is copied completely\n'.format(finish_time-t, new)
  lock.acquire()
  log_file = open('log.txt', 'at')
  log_file.write(finish_log)
  log_file.close()
  lock.release()


if __name__ == "__main__":
  start_program = timeit.default_timer()
  lock = threading.Lock()
  while True:
    old_file = input('Input the file name: ')
    if(old_file == 'exit'):
      break
    new_file = input('Input the new name:  ')

    #multi threading
    t = threading.Thread(target=send_file, args=(old_file, new_file, start_program))
    t.start()