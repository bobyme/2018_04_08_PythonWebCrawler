import smtplib
smtpObj=smtplib.SMTP('smtp.gmail.com',587)
smtpObj.ehlo()
smtpObj.starttls()
smtpObj.login('bobyme@gmail.com','dwcqblyzsqzsfxyz')
smtpObj.sendmail('bobyme@gmail.com','bobyme@gmail.com','Subject: pyton test \nuse pyton snd mail')
smtpObj.quit()