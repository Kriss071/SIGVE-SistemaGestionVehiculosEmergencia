package com.capstone.sigve.domain.usecase.auth

import com.capstone.sigve.domain.model.UserProfile
import com.capstone.sigve.domain.repository.AuthRepository
import javax.inject.Inject

class GetCurrentUserUseCase @Inject constructor(
    private val authRepository: AuthRepository
) {
    suspend operator fun invoke(): Result<UserProfile> {
        return authRepository.getCurrentUserProfile()
    }
}


