pipeline {
    agent any

    environment {
        IMAGE_NAME = "ai-model-deploy"
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')  // Jenkins credential ID
    }

    stages {

        stage('Checkout') {
            steps {
                // Repo ko Jenkins workspace mein le kar aana
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t $IMAGE_NAME:latest .'
            }
        }

        stage('Login to Docker Hub') {
            steps {
                sh 'echo $DOCKERHUB_CREDENTIALS_PSW | docker login -u $DOCKERHUB_CREDENTIALS_USR --password-stdin'
            }
        }

        stage('Push Image') {
            steps {
                sh 'docker tag $IMAGE_NAME:latest $DOCKERHUB_CREDENTIALS_USR/$IMAGE_NAME:latest'
                sh 'docker push $DOCKERHUB_CREDENTIALS_USR/$IMAGE_NAME:latest'
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh 'kubectl apply -f k8s/deployment.yaml'
                sh 'kubectl apply -f k8s/service.yaml'
            }
        }
    }

    post {
        success {
            echo 'Pipeline complete: image built, pushed, and deployed.'
        }
        failure {
            echo 'Pipeline failed. Check logs above.'
        }
    }
}
