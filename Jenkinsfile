pipeline {
    agent any
    
    triggers {
        githubPush()
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
                    docker run -d \
                        --name ${CONTAINER_NAME} \
                        --restart always \
                        -p 5000:5000 \
                        ${DOCKER_IMAGE} \
                        python3 app.py
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
                    docker run --rm \
                        --network host \
                        -e BASE_URL=http://localhost:5000 \
                        -v $(pwd)/test-results:/app/test-results \
                        ${DOCKER_IMAGE} \
                        python -m pytest tests/test_student_app.py \
                            -v \
                            --junit-xml=/app/test-results/results.xml
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
            script {
                // Get email of whoever pushed
                def pusherEmail = sh(
                    returnStdout: true,
                    script: "git log -1 --pretty=format:'%ae'"
                ).trim()

                echo "Sending email to: ${pusherEmail} and teacher"

                emailext(
                    subject: "${currentBuild.result ?: 'SUCCESS'} - Flask Student App Pipeline #${currentBuild.number}",
                    body: """
                        <h2>Pipeline Result: ${currentBuild.result ?: 'SUCCESS'}</h2>
                        <p><b>Job:</b> ${env.JOB_NAME}</p>
                        <p><b>Build Number:</b> #${env.BUILD_NUMBER}</p>
                        <p><b>Triggered by:</b> ${pusherEmail}</p>
                        <p><b>Build URL:</b> <a href="${env.BUILD_URL}">${env.BUILD_URL}</a></p>
                        <p><b>Git Commit:</b> ${env.GIT_COMMIT}</p>
                        <p><b>App URL:</b> <a href="http://13.51.44.221:5000">http://13.51.44.221:5000</a></p>
                    """,
                    to: "${pusherEmail}, qasimalik@gmail.com",
                    mimeType: 'text/html',
                    attachLog: true,
                    compressLog: true
                )
            }
        }
        
        success {
            echo 'Build and Tests Passed Successfully! App is running at http://13.51.44.221:5000'
        }
        
        failure {
            echo 'Build Failed!'
        }
    }
}
