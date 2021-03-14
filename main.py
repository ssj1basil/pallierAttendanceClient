import requests as rq
from client_logic import encrypt_plain_array, public_key, private_key
from bottle import route, get, post, run, request, redirect
import pickle
import math


@route('/')
def front_page():
    return 'welcome to attendance management system'


# this is for getting data from fingerprint
@get('/mark')
def mark_attendance():
    return '''
        <form action="/mark" method="post" enctype="multipart/form-data">
            roll_number: <input name="roll_number" type="text" />
            fingerprint: <input name="fingerprint" type="file" />
            <input value="Mark Attendance" type="submit" />
        </form>
    '''


# incomplete
@post('/mark')
def do_mark():
    # get roll number
    roll_number = request.forms.get('roll_number')
    # get finger print string from a file and expects txt file with comma seperted values
    fingerprint_string = request.files.fingerprint.file.read().decode(
        'ascii').rstrip()
    # convert it to fingerprint array
    fingerprint_plain = list(map(int, fingerprint_string.split(",")))
    enc_fingerprint = encrypt_plain_array(fingerprint_plain, public_key)

    #we have to send  the public key for verification or only the two object are enough to do the homomorphic operation
    print("from mark -> ",fingerprint_plain, enc_fingerprint)
    print("from mark -> ",roll_number)
    send_data = {"roll_number": roll_number, "fingerprint": enc_fingerprint}

    data = pickle.dumps(send_data, protocol=2)
    url = "https://pallierAttendanceSever.justinepdevasia.repl.co/mark"
    send_data = rq.post(url, data=data)
    if send_data.status_code == 200:
      # redirect('/verification')
      return 'mark send'
    else:
      print("unsuccessfull")
      return 'mark failure'


# this is for getting register details from local system
@get('/register')
def register():
    return '''
        <form action="/register" method="post" enctype="multipart/form-data">
            roll_number: <input name="roll_number" type="text" />
            fingerprint: <input name="fingerprint" type="file" />
            <input value="Register" type="submit" />
        </form>
    '''


# this for sending register details to server
@post('/register')
def do_register():
    # get roll number
    roll_number = request.forms.get('roll_number')
    # get finger print string from a file, expects txt file with comma seperated values 1,2,3,4
    fingerprint_string = request.files.fingerprint.file.read().decode(
        'ascii').rstrip()
    # convert it to fingerprint array
    fingerprint_plain = list(map(int, fingerprint_string.split(",")))
    #calculate fingerprint inverse
    N = 1000
    finger_print_inverse = [N - i for i in fingerprint_plain]
    # encrypt the finger print
    enc_fingerprint = encrypt_plain_array(finger_print_inverse, public_key)
    print("from register -> ",fingerprint_plain, enc_fingerprint)
    print("from register -> ",roll_number)

    # we store roll number and fingerprint to a dictionary
    send_data = {"roll_number": roll_number, "fingerprint": enc_fingerprint}
    # pickle the dictionary
    data = pickle.dumps(send_data, protocol=2)

    # this is the url of the remote server for registration
    url = "https://pallierAttendanceSever.justinepdevasia.repl.co/register"
    # we send the pickled data as post request
    send_data = rq.post(url, data=data)
    # if request successfully reached server
    if send_data.status_code == 200:
        return "<p>Registraton Successful</p>"
    else:
        return "<p>Registration failed.</p>"


@route('/verification', method=['POST'])
def verification():
    if request.method == 'POST':
        request_data = request.body.read()
        unpickled_data = pickle.loads(request_data)
        roll_number = unpickled_data['roll_number']
        sum_fingerprint = unpickled_data['fingerprint']
        # decryped fingerprint sum
        print(sum_fingerprint)
        plain_sum_fingerprint = [
            private_key.decrypt(x) for x in sum_fingerprint
        ]
        print("plain fingerprint sum ",plain_sum_fingerprint)
        N = 1000
        plain_sum_fingerprint = [x % N for x in plain_sum_fingerprint]
        threshold = 2
        output = [min(x, N - x) for x in plain_sum_fingerprint]

        for x, y in zip(*[iter(output)] * 2):
            if math.sqrt(x * x + y * y) > threshold:
                print("Verfication failed")

        print("Verfication successfull")

        file = open("attendance.txt", "a+")
        file.write(roll_number + " Present")

    #elif request.method == 'GET':
        #return 'you are in verification'
@post('/test')
def test():
    request_data = request.body.read()
    unpickled_data = pickle.loads(request_data)
    roll_number = unpickled_data['roll_number']
    # sum_fingerprint = unpickled_data['fingerprint']
    print(roll_number)
    return 'test'


run(host='0.0.0.0', port=8080, debug=True)
