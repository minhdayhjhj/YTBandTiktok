import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { VideoReuploadToolComponent } from './components/video-reupload-tool/video-reupload-tool.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, VideoReuploadToolComponent],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'Video Reupload Tool Pro';
}