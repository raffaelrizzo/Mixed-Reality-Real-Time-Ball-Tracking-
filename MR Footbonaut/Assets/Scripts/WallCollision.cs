using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class WallCollision : MonoBehaviour
{
    public GameObject scoreManagerObject;
    public AudioClip hitSound; // Sound when the target is hit
    public AudioClip missSound; // Sound when the target is not hit

    private AudioSource audioSource;

    private void Start()
    {
        // Get the AudioSource component
        audioSource = GetComponent<AudioSource>();
    }

    private void OnCollisionEnter(Collision collision)
    {
        if (collision.gameObject.CompareTag("SoccerWall"))
        {
            Cube cube = collision.gameObject.GetComponent<Cube>();
            if (cube != null)
            {
                if (cube.IsLit())
                {
                    ScoreManager scoreManager = scoreManagerObject.GetComponent<ScoreManager>();
                    if (scoreManager != null)
                    {
                        scoreManager.IncreaseScore();
                    }

                    // Play the hit sound
                    audioSource.PlayOneShot(hitSound);

                    // Optionally, turn off the cube's light when it gets hit
                    cube.TurnOffLight();
                }
                else
                {
                    // Play the miss sound
                    audioSource.PlayOneShot(missSound);
                }
            }
        }
    }
}
