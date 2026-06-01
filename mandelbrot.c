#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define WIDTH 800
#define HEIGHT 600
#define MAX_ITER 10000

#define TAG_TASK 1
#define TAG_RESULT 2
#define TAG_STOP 3

typedef struct
{
    int start_row;
    int num_rows;
} Task;

int mandelbrot(double real, double imag)
{
    double z_real = 0.0;
    double z_imag = 0.0;

    int iter = 0;

    while ((z_real * z_real + z_imag * z_imag <= 4.0) &&
           iter < MAX_ITER)
    {

        double temp = z_real * z_real - z_imag * z_imag + real;

        z_imag = 2.0 * z_real * z_imag + imag;
        z_real = temp;

        iter++;
    }

    return iter;
}

void save_ppm(const char *filename, int *image)
{
    FILE *fp = fopen(filename, "w");

    fprintf(fp, "P3\n");
    fprintf(fp, "%d %d\n", WIDTH, HEIGHT);
    fprintf(fp, "255\n");

    for (int i = 0; i < WIDTH * HEIGHT; i++)
    {

        int color = (image[i] * 255) / MAX_ITER;

        fprintf(fp, "%d %d %d ",
                color,
                color,
                color);

        if ((i + 1) % WIDTH == 0)
            fprintf(fp, "\n");
    }

    fclose(fp);
}

int main(int argc, char *argv[])
{

    MPI_Init(&argc, &argv);

    int rank, size;
    double start, end;

    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    // =========================
    // COORDENADOR
    // =========================

    if (rank == 0)
    {
        start = MPI_Wtime();

        int *image = malloc(sizeof(int) * WIDTH * HEIGHT);

        int next_row = 0;
        int rows_per_task = 10;

        MPI_Status status;

        // envia tarefas iniciais
        for (int worker = 1; worker < size; worker++)
        {

            if (next_row >= HEIGHT)
                break;

            Task task;

            task.start_row = next_row;
            task.num_rows = rows_per_task;

            MPI_Send(&task,
                     sizeof(Task),
                     MPI_BYTE,
                     worker,
                     TAG_TASK,
                     MPI_COMM_WORLD);

            next_row += rows_per_task;
        }

        int rows_completed = 0;

        while (rows_completed < HEIGHT)
        {

            Task result_task;

            MPI_Recv(&result_task,
                     sizeof(Task),
                     MPI_BYTE,
                     MPI_ANY_SOURCE,
                     TAG_RESULT,
                     MPI_COMM_WORLD,
                     &status);

            int worker = status.MPI_SOURCE;

            int pixels =
                result_task.num_rows * WIDTH;

            MPI_Recv(
                &image[result_task.start_row * WIDTH],
                pixels,
                MPI_INT,
                worker,
                TAG_RESULT,
                MPI_COMM_WORLD,
                &status);

            rows_completed += result_task.num_rows;

            // envia nova tarefa
            if (next_row < HEIGHT)
            {

                Task task;

                task.start_row = next_row;
                task.num_rows = rows_per_task;

                if (next_row + rows_per_task > HEIGHT)
                    task.num_rows = HEIGHT - next_row;

                MPI_Send(&task,
                         sizeof(Task),
                         MPI_BYTE,
                         worker,
                         TAG_TASK,
                         MPI_COMM_WORLD);

                next_row += task.num_rows;
            }
            else
            {

                Task stop_task;

                MPI_Send(&stop_task,
                         sizeof(Task),
                         MPI_BYTE,
                         worker,
                         TAG_STOP,
                         MPI_COMM_WORLD);
            }
        }

        end = MPI_Wtime();

        save_ppm("mandelbrot.ppm", image);

        free(image);

        printf("Imagem salva em mandelbrot.ppm\n");
        printf("Tempo total: %f segundos\n", end - start);
    }

    // =========================
    // WORKERS
    // =========================

    else
    {

        MPI_Status status;

        while (1)
        {

            Task task;

            MPI_Recv(&task,
                     sizeof(Task),
                     MPI_BYTE,
                     0,
                     MPI_ANY_TAG,
                     MPI_COMM_WORLD,
                     &status);

            if (status.MPI_TAG == TAG_STOP)
                break;

            int *buffer =
                malloc(sizeof(int) *
                       task.num_rows *
                       WIDTH);

            for (int row = 0; row < task.num_rows; row++)
            {

                int y = task.start_row + row;

                for (int x = 0; x < WIDTH; x++)
                {

                    double real =
                        -2.5 + (3.5 * x / WIDTH);

                    double imag =
                        -1.0 + (2.0 * y / HEIGHT);

                    int iter =
                        mandelbrot(real, imag);

                    buffer[row * WIDTH + x] =
                        iter;
                }
            }

            MPI_Send(&task,
                     sizeof(Task),
                     MPI_BYTE,
                     0,
                     TAG_RESULT,
                     MPI_COMM_WORLD);

            MPI_Send(buffer,
                     task.num_rows * WIDTH,
                     MPI_INT,
                     0,
                     TAG_RESULT,
                     MPI_COMM_WORLD);

            free(buffer);
        }
    }

    MPI_Finalize();

    return 0;
}