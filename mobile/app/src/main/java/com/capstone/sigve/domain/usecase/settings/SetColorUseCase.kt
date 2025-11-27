package com.capstone.sigve.domain.usecase.settings

import com.capstone.sigve.domain.model.AppColor
import com.capstone.sigve.domain.repository.SettingsRepository
import javax.inject.Inject

class SetColorUseCase @Inject constructor(
    private val settingsRepository: SettingsRepository
) {
    suspend operator fun invoke(color: AppColor) {
        settingsRepository.setColor(color)
    }
}

