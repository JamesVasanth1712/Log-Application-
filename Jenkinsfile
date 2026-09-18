pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out Log Application...'

                git branch: 'main',
                    url: 'https://github.com/JamesVasanth1712/Log-Application-.git'
            }
        }

        stage('Project Check') {
            steps {
                echo 'Checking project structure...'

                sh 'pwd'
                sh 'ls -la'

                sh 'python3 --version'
                sh 'python3 -m pip --version'

                sh 'docker --version'
                sh 'docker compose version'
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Creating Python virtual environment...'

                sh 'rm -rf .jenkins-venv'
                sh 'python3 -m venv .jenkins-venv'

                echo 'Installing Python dependencies...'

                sh '.jenkins-venv/bin/python -m pip install --upgrade pip'
                sh '.jenkins-venv/bin/python -m pip install -r requirements.txt'
            }
        }

        stage('Python Syntax Check') {
            steps {
                echo 'Checking Python syntax...'

                sh '.jenkins-venv/bin/python -m py_compile finalapp.py'
            }
        }

        stage('Flask Import Check') {
            steps {
                echo 'Checking Flask application...'

                sh '''
                    .jenkins-venv/bin/python -c "import finalapp; print('Flask application imported successfully')"
                '''
            }
        }

        stage('Docker Build') {
            steps {
                echo 'Building Docker image...'

                sh 'docker build -t log-application:ci .'
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deploying Log Application...'

                sh 'docker rm -f log-application || true'

                sh 'docker run -d --name log-application -p 5000:5000 log-application:ci'
            }
        }

        stage('Health Check') {
            steps {
                echo 'Checking Log Application health...'

                sh '''
                    sleep 5

                    docker exec log-application python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/', timeout=5); print('Log Application is healthy')"
                '''
            }
        }
    }

    post {

        success {
            echo '=========================================='
            echo 'Log Application CI/CD SUCCESS'
            echo '=========================================='
            echo 'Application deployed on port 5000'
            echo 'Open: http://localhost:5000'
            echo '=========================================='
        }

        failure {
            echo '=========================================='
            echo 'Log Application CI/CD FAILED'
            echo 'Check Console Output.'
            echo '=========================================='
        }

        always {
            echo 'CI/CD Pipeline execution completed.'
        }
    }
}