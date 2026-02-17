package com.music.recommendation.screens

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.music.recommendation.api.MusicRepository
import com.music.recommendation.api.Result
import kotlinx.coroutines.launch

class AuthViewModel : ViewModel() {
    private val repository = MusicRepository()

    var isLoading by mutableStateOf(false)
    var error by mutableStateOf<String?>(null)
    var isLoggedIn by mutableStateOf(false)
    var currentUser by mutableStateOf<String?>(null)

    fun login(username: String, password: String) {
        viewModelScope.launch {
            isLoading = true
            error = null

            when (val result = repository.login(username, password)) {
                is Result.Success -> {
                    isLoggedIn = true
                    currentUser = username
                }
                is Result.Error -> {
                    error = result.message
                }
                is Result.Loading -> {}
            }
            isLoading = false
        }
    }

    fun register(username: String, email: String, password: String) {
        viewModelScope.launch {
            isLoading = true
            error = null

            when (val result = repository.register(username, email, password)) {
                is Result.Success -> {
                    // Auto login after register
                    login(username, password)
                }
                is Result.Error -> {
                    error = result.message
                }
                is Result.Loading -> {}
            }
            isLoading = false
        }
    }

    fun logout() {
        repository.logout()
        isLoggedIn = false
        currentUser = null
    }

    fun clearError() {
        error = null
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LoginScreen(
    viewModel: AuthViewModel,
    onLoginSuccess: () -> Unit
) {
    var isLoginMode by remember { mutableStateOf(true) }
    var username by remember { mutableStateOf("") }
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }

    LaunchedEffect(viewModel.isLoggedIn) {
        if (viewModel.isLoggedIn) {
            onLoginSuccess()
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = "Music Recommendation",
            style = MaterialTheme.typography.headlineMedium
        )

        Spacer(modifier = Modifier.height(8.dp))

        Text(
            text = if (isLoginMode) "Login" else "Register",
            style = MaterialTheme.typography.titleLarge
        )

        Spacer(modifier = Modifier.height(32.dp))

        OutlinedTextField(
            value = username,
            onValueChange = { username = it },
            label = { Text("Username") },
            singleLine = true,
            modifier = Modifier.fillMaxWidth()
        )

        if (!isLoginMode) {
            Spacer(modifier = Modifier.height(16.dp))
            OutlinedTextField(
                value = email,
                onValueChange = { email = it },
                label = { Text("Email") },
                singleLine = true,
                modifier = Modifier.fillMaxWidth()
            )
        }

        Spacer(modifier = Modifier.height(16.dp))

        OutlinedTextField(
            value = password,
            onValueChange = { password = it },
            label = { Text("Password") },
            singleLine = true,
            visualTransformation = PasswordVisualTransformation(),
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(24.dp))

        viewModel.error?.let { error ->
            Text(
                text = error,
                color = MaterialTheme.colorScheme.error,
                style = MaterialTheme.typography.bodySmall
            )
            Spacer(modifier = Modifier.height(8.dp))
        }

        Button(
            onClick = {
                viewModel.clearError()
                if (isLoginMode) {
                    viewModel.login(username, password)
                } else {
                    viewModel.register(username, email, password)
                }
            },
            enabled = !viewModel.isLoading && username.isNotBlank() && password.isNotBlank(),
            modifier = Modifier.fillMaxWidth()
        ) {
            if (viewModel.isLoading) {
                CircularProgressIndicator(
                    modifier = Modifier.size(20.dp),
                    color = MaterialTheme.colorScheme.onPrimary
                )
            } else {
                Text(if (isLoginMode) "Login" else "Register")
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        TextButton(onClick = { isLoginMode = !isLoginMode }) {
            Text(
                if (isLoginMode) "Don't have an account? Register"
                else "Already have an account? Login"
            )
        }
    }
}
