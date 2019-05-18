auth_port = 8081
nginx_port = 8087
ml_port = 5342
data_port = 5343
back_ip = '10.3.75.73'
ip = '0.0.0.0'
protocol = 'http'

nginx_url = f'{protocol}://{ip}:{nginx_port}'
auth_url = f'{protocol}://{ip}:{nginx_port}'
ml_url = f'{protocol}://{back_ip}:{ml_port}'
data_url = f'{protocol}://{back_ip}:{data_port}'
