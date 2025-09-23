import { Component, computed, inject, ChangeDetectionStrategy } from '@angular/core';
import { SecurityService } from '../../services/security.service';
import { CommonModule, DatePipe } from '@angular/common';

@Component({
  selector: 'app-ban-screen',
  template: `
    <div class="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50 text-white font-mono">
      <div class="text-center">
        <h1 class="text-6xl text-red-500 mb-4 animate-pulse">ACCESS DENIED</h1>
        <p class="text-xl mb-2">Your activities have been flagged as suspicious.</p>
        <p class="text-lg mb-8">Please close developer tools and refrain from right-clicking.</p>
        <p class="text-2xl">Ban lifts in: <span class="font-bold text-yellow-400">{{ formattedTimeRemaining() }}</span></p>
      </div>
    </div>
  `,
  standalone: true,
  imports: [CommonModule],
  providers: [DatePipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class BanScreenComponent {
  private securityService = inject(SecurityService);
  private datePipe = inject(DatePipe);

  // Fix: Use the signal from the security service
  banTimeRemaining = this.securityService.banTimeRemaining;

  formattedTimeRemaining = computed(() => {
    const remaining = this.banTimeRemaining();
    // Use DatePipe to format. It expects a Date object or timestamp. 
    // Creating a date at epoch and setting UTC time to remaining milliseconds.
    return this.datePipe.transform(remaining, 'mm:ss', 'UTC');
  });
}
