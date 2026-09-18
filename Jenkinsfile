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
                echo 'Installing Python dependencies...'

                sh 'python3 -m pip install --upgrade pip'
                sh 'python3 -m pip install -r requirements.txt'
            }
        }

        stage('Python Syntax Check') {
            steps {
                echo 'Checking Python syntax...'

                sh 'python3 -m py_compile finalapp.py'
            }
        }

        stage('Flask Import Check') {
            steps {
                echo 'Checking Flask application...'

                sh '''
                    python3 -c "import finalapp; print('Flask application imported successfully')"
                '''
            }
        }

        stage('Docker Build') {
            steps {
                echo 'Building Docker image...'

                sh 'docker build -t log-application:ci .'
            }
        }
    }

    post {

        success {
            echo '=========================================='
            echo 'Log Application CI SUCCESS'
            echo '=========================================='
        }

        failure {
            echo '=========================================='
            echo 'Log Application CI FAILED'
            echo 'Check Console Output.'
            echo '=========================================='
        }

        always {
            echo 'CI Pipeline execution completed.'
        }
    }
}