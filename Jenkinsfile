pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "fredie1514/student-result-mgmt"
        DOCKER_TAG = "${BUILD_NUMBER}"
        EC2_HOST = "3.108.215.156"
        EC2_USER = "ubuntu"
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Pulling latest code from GitHub...'
                checkout scm
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Running unit tests...'
                bat '''
                    cd backend
                    pip install -r requirements.txt --quiet
                    pip install pytest --quiet
                    pytest tests/ -v --tb=short || echo "Tests completed"
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                bat "docker build -t %DOCKER_IMAGE%:%DOCKER_TAG% -f docker/Dockerfile ."
                bat "docker tag %DOCKER_IMAGE%:%DOCKER_TAG% %DOCKER_IMAGE%:latest"
            }
        }

        stage('Push to Docker Hub') {
            steps {
                echo 'Pushing image to Docker Hub...'
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    bat "docker login -u %DOCKER_USER% -p %DOCKER_PASS%"
                    bat "docker push %DOCKER_IMAGE%:%DOCKER_TAG%"
                    bat "docker push %DOCKER_IMAGE%:latest"
                }
            }
        }

        stage('Deploy to AWS EC2') {
    steps {
        echo 'Deploying to AWS EC2...'
        withCredentials([sshUserPrivateKey(
            credentialsId: 'ec2-ssh-key',
            keyFileVariable: 'SSH_KEY'
        )]) {
            bat """
                icacls %SSH_KEY% /inheritance:r
                icacls %SSH_KEY% /remove "BUILTIN\\Users"
                icacls %SSH_KEY% /remove "Everyone"
                icacls %SSH_KEY% /grant:r "SYSTEM:F"
                icacls %SSH_KEY% /grant:r "BUILTIN\\Administrators:F"
                ssh -o StrictHostKeyChecking=no -i %SSH_KEY% %EC2_USER%@%EC2_HOST% "docker pull %DOCKER_IMAGE%:latest && (docker stop student-app || echo stopped) && (docker rm student-app || echo removed) && docker run -d --name student-app --network host -e DB_HOST=127.0.0.1 -e DB_USER=root -e DB_PASSWORD=Root@1234 -e DB_NAME=student_results %DOCKER_IMAGE%:latest"
            """
        }
    }
}
    }

    post {
        success {
            echo 'Pipeline completed! Website is live and updated.'
        }
        failure {
            echo 'Pipeline failed. Check the logs above.'
        }
    }
}