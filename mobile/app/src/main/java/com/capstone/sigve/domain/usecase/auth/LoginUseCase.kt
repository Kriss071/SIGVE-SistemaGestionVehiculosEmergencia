package com.capstone.sigve.domain.usecase.auth

import com.capstone.sigve.domain.repository.AuthRepository
import javax.inject.Inject

class LoginUseCase @Inject constructor(
    private val authRepository: AuthRepository
) {
    suspend operator fun invoke(email: String, password: String): Result<Unit> {
        return authRepository.signIn(email, password)
    }
}

