import { Component, ElementRef, inject, AfterViewInit, OnDestroy, ChangeDetectionStrategy } from '@angular/core';

@Component({
  selector: 'app-effects',
  template: `<canvas class="fixed top-0 left-0 w-full h-full -z-10 opacity-30"></canvas>`,
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class EffectsComponent implements AfterViewInit, OnDestroy {
  private elementRef = inject(ElementRef);
  private canvas!: HTMLCanvasElement;
  private ctx!: CanvasRenderingContext2D;
  private columns!: number;
  private drops: number[] = [];
  private animationFrameId: number | null = null;
  // Fix: Use a character set for the digital rain effect
  private readonly characters = '0123456789';
  private readonly fontSize = 16;

  ngAfterViewInit() {
    this.canvas = this.elementRef.nativeElement.querySelector('canvas');
    if (this.canvas) {
        this.ctx = this.canvas.getContext('2d')!;
        this.setup();
        window.addEventListener('resize', this.setup);
        this.animate();
    }
  }

  ngOnDestroy() {
    window.removeEventListener('resize', this.setup);
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
    }
  }

  private setup = () => {
    this.canvas.width = window.innerWidth;
    this.canvas.height = window.innerHeight;
    this.columns = Math.floor(this.canvas.width / this.fontSize);
    this.drops = [];
    for (let i = 0; i < this.columns; i++) {
      this.drops[i] = 1;
    }
  };

  private draw = () => {
    this.ctx.fillStyle = 'rgba(0, 0, 0, 0.04)';
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

    this.ctx.fillStyle = '#0f0'; // Green text
    this.ctx.font = `${this.fontSize}px monospace`;

    for (let i = 0; i < this.drops.length; i++) {
      const text = this.characters.charAt(Math.floor(Math.random() * this.characters.length));
      this.ctx.fillText(text, i * this.fontSize, this.drops[i] * this.fontSize);

      if (this.drops[i] * this.fontSize > this.canvas.height && Math.random() > 0.975) {
        this.drops[i] = 0;
      }
      this.drops[i]++;
    }
  };

  private animate = () => {
    this.draw();
    this.animationFrameId = requestAnimationFrame(this.animate);
  };
}
