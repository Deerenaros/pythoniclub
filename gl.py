## A sample of opengl using with pygame
## Thanks to @luke-kelly at stackoverflow
## https://stackoverflow.com/questions/56122387/rendering-image-in-pygame-using-pyopengl

import pygame
from OpenGL.GL import *
from OpenGL.GL import shaders
import unittest
import numpy as np
from ctypes import sizeof, c_float, c_void_p


def updateSplash(image):
    width = image.get_width()
    height = image.get_height()
    image_data = pygame.image.tostring(image, "RGBA", True)
    mip_map_level = 0
    glTexImage2D(GL_TEXTURE_2D, mip_map_level, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)


def renderSplash(image, cmap=f"{{ {','.join('vec4(%f,%f,%f,1)' % (col/255, col/255, col/255) for col in range(0, 256))} }}"):
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    vertex_data = np.array([-1, -1, 0, 0,  -1, 1, 0, 1,  1, 1, 1, 1,  -1, -1, 0, 0,  1, 1, 1, 1,  1, -1, 1, 0], np.float32)
    glBufferData(GL_ARRAY_BUFFER, vertex_data, GL_STATIC_DRAW)
    vertex_position_attribute_location = 0
    uv_attribute_location = 1
    glVertexAttribPointer(vertex_position_attribute_location, 2, GL_FLOAT, GL_FALSE, sizeof(c_float)*4, c_void_p(0))
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(uv_attribute_location, 2, GL_FLOAT, GL_FALSE, sizeof(c_float)*4, c_void_p(sizeof(c_float)*2))
    glEnableVertexAttribArray(1)
    
    image_texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, image_texture)

    updateSplash(image)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

    vertex_shader = shaders.compileShader("""
        #version 330
        layout(location = 0) in vec2 pos;
        layout(location = 1) in vec2 uvIn;
        out vec2 uv;
        void main() {
            gl_Position = vec4(pos, 0, 1);
            uv = uvIn;
        }
        """, GL_VERTEX_SHADER)

    fragment_shader = shaders.compileShader(f"""
        #version 330
        out vec4 fragColor;
        in vec2 uv;
        uniform sampler2D tex;
        uniform vec4 cmap[256] = {cmap};
        int i;
        void main() {{
            // i = int(texture(tex, uv).r * 255);
            // fragColor = cmap[i];
            fragColor = texture(tex, uv);
        }}
    """, GL_FRAGMENT_SHADER)

    shader_program = shaders.compileProgram(vertex_shader, fragment_shader)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glUseProgram(shader_program)
    glDrawArrays(GL_TRIANGLES, 0, 6)

def main():
    pygame.quit()
    pygame.init()
    image = pygame.image.load("Background.jpg")

    width = image.get_width()
    height = image.get_height()
    width = 720
    height = 480
    size = (width,height)
    pygame.display.set_mode(size, pygame.OPENGL | pygame.DOUBLEBUF | pygame.HWSURFACE)
    glViewport(0, 0, width, height)

    renderSplash(image)
    pygame.display.flip()
    close_window()

def close_window():
    key_pressed = False
    while not key_pressed:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                key_pressed = True

if __name__ == "__main__":
    main()
