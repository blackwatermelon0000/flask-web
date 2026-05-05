pipeline {
    agent any
    
    triggers {
        githubPush()        // This enables automatic trigger on GitHub push
    }
    
    environment {
        DOCKER_IMAGE = 'student-app-test'
        CONTAINER_NAME = 'student-app'
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo '=== Pulling code from GitHub ==='
                checkout scm
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo '=== Building Docker image ==='
                sh 'docker build -t ${DOCKER_IMAGE} .'
            }
        }
        
        stage('Start Application') {
            steps {
                echo '=== Starting Flask application ==='
                sh '''
                    docker rm -f ${CONTAINER_NAME} || true
                    docker run -d --name ${CONTAINER_NAME} -p 5000:5000 ${DOCKER_IMAGE} python3 app.py
                '''
                echo 'Waiting for app to be ready...'
                sleep 10
            }
        }
        
        stage('Run Tests') {
            steps {
                echo '=== Running Selenium test cases ==='
                sh '''
                    mkdir -p test-results
                    docker run --rm --name selenium-tests \
                        --network host \
                        -v $(pwd)/test-results:/app/test-results \
                        -e BASE_URL=http://localhost:5000 \
                        ${DOCKER_IMAGE} \
                        python -m pytest tests/test_student_app.py -v --junit-xml=/app/test-results/results.xml
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'test-results/**', allowEmptyArchive: true
                    junit testResults: 'test-results/results.xml',
                          allowEmptyResults: true,
                          skipPublishingChecks: true
                }
            }
        }
    }
    
    post {
        always {
            echo '=== Cleaning up ==='
            sh '''
                docker rm -f ${CONTAINER_NAME} || true
                docker rm -f selenium-tests || true
            '''
            
            // Email Notification
            emailext (
                subject: "${currentBuild.result ?: 'SUCCESS'} - Flask Student App Pipeline #${currentBuild.number}",
                body: '''
                    <h2>Pipeline Build ${currentBuild.result}</h2>
                    <p><b>Job:</b> ${JOB_NAME}</p>
                    <p><b>Build Number:</b> #${BUILD_NUMBER}</p>
                    <p><b>Check Console Output:</b> <a href="${BUILD_URL}">${BUILD_URL}</a></p>
                    <p><b>Git Commit:</b> ${GIT_COMMIT}</p>
                ''',
                to: 'amauua587453@gmail.com',
                attachLog: true,
                compressLog: true
            )
        }
        
        success {
            echo 'Build and Tests Passed Successfully!'
        }
        
        failure {
            echo 'Build Failed!'
        }
    }
}
