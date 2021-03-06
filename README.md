
## WARNING: After better validating the idea of this prototype I think it's not a good idea.

### What is Passpod?

*Passpod* is a library that hashes and saves passwords in a safe way.
It is still a prototype, do not use in production. Feedback very welcome.

**How currently web platforms save passwords**

| User           | Password Hash |
| -------------- | ------------- |
| BieberLover93  | 356a192b79... |
| EnterpriseUser | da4b9237ba... |
| iorfsjadk      | 77de68daec... |
|      ...       |      ...      |

**How *Passpod* saves passwords**

| Hash           |
| -------------- |
| 1b645389247... |
| ac3478d69a3... |
| c1dfd96eea8... |
| 902ba3cda18... |
|      ...       |

The idea is to minimize the harm that a compromised password database may cause.
A leaked *Passpod* database does not contain a direct link between a user name and its hashed password, this makes brute force attacks more expensive.
Additionally when sufficient dummy hash entries are created, it is difficult to get the approximate number of registered users, or any other information.

The design of *Passpod* also encourages the use of a separate database for password storage,
this prevents SQL injections attacks targeting the application to compromise the hashed passwords.

Often password hashing is implemented on the fly and bundled with application code,
*Passpod* hopes to offer an modularized, better reviewed, more secure alternative to this.

### How To Use It

*Passpod* offers a Python library with a simple dictionary-like interface.
```python
>>> from passpod impor passpod
>>> passwords = passpod.open('sqlite:///tmp/mydb', namespace='RyHoJI...') # passwords is a dictionary-like object
>>> psswords['user1'] = 'mypassword$*!'
>>> 'user1' in passwords
True
>>> passwords['user1'] == 'mypassword$*!'
True
>>> del passwords['user1']
```

### Licence
*Passpod* is licensed under the The MIT License (MIT)
